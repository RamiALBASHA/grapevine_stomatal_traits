# -*- coding: utf-8 -*-
"""This module performs a complete comutation scheme: irradiance absorption, gas-exchange, hydraulic structure,
energy-exchange, and soil water depletion, for each given time step.
"""
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from hydroshoot import (architecture, solver, io)
from hydroshoot.energy import calc_effective_sky_temperature
from hydroshoot.initialisation import init_model, init_hourly, set_collar_water_potential_function
from openalea.mtg.mtg import MTG
from openalea.plantgl.all import Scene, surface
from pandas import DataFrame

from grapevine_stomatal_traits.simulator.inputs import HydroShootHourlyInputs
from grapevine_stomatal_traits.simulator.irrigation import handle_irrigation


def run(g: MTG, wd: Path, params: dict, scene: Scene = None, write_result: bool = True, path_output: Path = None,
        is_save_mtg: bool = True, **kwargs) -> DataFrame:
    """Calculates leaf gas and energy exchange in addition to the hydraulic structure of an individual plant.

    Args:
        g: mtg object
        wd: working directory
        params: user params
        scene: PlantGl scene (default None)
        write_result: if True then hourly plant-scale outputs are written into a CSV file
        path_output: summary data output file path
        is_save_mtg: True to save the mtg object (default False)
        kwargs: can include:
            psi_soil_init (float): [MPa] initial soil water potential
            psi_soil (float): [MPa] predawn soil water potential
            gdd_since_budbreak (float): [°Cd] growing degree-day since bubreak
            sun2scene (Scene): PlantGl scene, when prodivided, a sun object (sphere) is added to it
            soil_size (float): [cm] length of squared mesh size
            leaf_nitrogen (dict): leaf nitrogen content per area (key=(int) mtg leaf vertex, value=(float) nitrogen content)
            leaf_ppfd (dict of dict): incident and absorbed PPFD by each leaf per each simulated hour
                key:(datetime) simulated datetime, value:
                    key:'Ei', value: (key: (int) mtg leaf vertex, value: (incident PPFD)),
                    key:'Eabs', value: (key: (int) mtg leaf vertex, value: (absorbed PPFD))
            form_factors (dict of dict): form factors for the sky, leaves and the soil
                key=(str) one of ('ff_sky', 'ff_leaves', 'ff_soil'), value=(key=(int) mtg leaf vertex, value=(form factor)
            drip_rate (float): nominal drip rate (kg h-1)
            replacement_fraction (float): fraction of plant water requirements fulfillment
                (0 for no irrigation, 1 for complete fulfillment)
            irrigation_freq (int): number of days between two consecutive irrigations


    Returns:
        Absorbed whole plant global irradiance (Rg), net photosynthesis (An), transpiration (E) and
            median leaf temperature (Tleaf)

    """
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('+ Project: ', wd)
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    time_on = datetime.now()

    # Read user parameters
    inputs = io.HydroShootInputs(
        path_project=wd,
        user_params=params,
        scene=scene,
        is_write_result=write_result,
        path_output_file=path_output,
        **kwargs)
    io.verify_inputs(g=g, inputs=inputs)
    params = inputs.params

    # ==============================================================================
    # Initialisation
    # ==============================================================================
    time_conv = params.simulation.conv_to_second
    io.print_sim_infos(inputs=inputs)
    g = init_model(g=g, inputs=inputs)

    irrigation_rate = 0.
    irrigation_remain = 0.
    if any([k in kwargs for k in ('irrigation_freq', 'drip_rate', 'replacement_fraction')]):
        is_irrigation = True
        drip_rate = kwargs['drip_rate']
        replacement_fraction = kwargs['replacement_fraction']
        irrigation_freq = kwargs['irrigation_freq']
        date_start_irrigation = params.simulation.date_beg + timedelta(days=irrigation_freq)
    else:
        is_irrigation = False
        drip_rate = None
        replacement_fraction = None
        irrigation_freq = None
        date_start_irrigation = None

    is_psi_soil_forced = True if inputs.psi_soil_forced is not None else False
    if is_psi_soil_forced:
        psi_soil = inputs.psi_soil_forced
    elif 'psi_soil_init' in kwargs:
        psi_soil = kwargs['psi_soil_init']
    else:
        psi_soil = None

    calc_collar_water_potential = set_collar_water_potential_function(params=params)

    # ==============================================================================
    # Simulations
    # ==============================================================================

    sapflow = []
    an_ls = []
    rg_ls = []
    irrigation_ls = []
    psi_soil_ls = []
    psi_collar_ls = []
    psi_leaf_ls = []
    leaf_temperature_dict = {}

    # The time loop +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    inputs_hourly = HydroShootHourlyInputs(
        psi_soil=psi_soil, sun2scene=inputs.sun2scene, is_psi_soil_forced=is_psi_soil_forced)

    for date in params.simulation.date_range:
        print("=" * 72)
        print(f'Date: {date}\n')
        if is_irrigation:
            if date >= date_start_irrigation:
                irrigation_rate, irrigation_remain = handle_irrigation(
                    date_sim=date,
                    date_start_irrigation=date_start_irrigation,
                    irrigation_freq=irrigation_freq,
                    sapflow=sapflow,
                    drip_rate=drip_rate,
                    replacement_fraction=replacement_fraction,
                    irrigation_to_apply=irrigation_remain)
            else:
                irrigation_rate = 0
                irrigation_remain = 0
        irrigation_ls.append(irrigation_rate)

        inputs_hourly.update(g=g, date_sim=date, hourly_weather=inputs.weather[inputs.weather.index == date],
                             psi_pd=inputs.psi_pd, params=params, water_input=irrigation_rate)

        g, diffuse_to_total_irradiance_ratio = init_hourly(
            g=g, inputs_hourly=inputs_hourly, leaf_ppfd=inputs.leaf_ppfd, params=params)

        inputs_hourly.sky_temperature = calc_effective_sky_temperature(
            diffuse_to_total_irradiance_ratio=diffuse_to_total_irradiance_ratio,
            temperature_cloud=params.energy.t_cloud,
            temperature_sky=params.energy.t_sky)

        solver.solve_interactions(
            g=g, meteo=inputs_hourly.weather.loc[date], psi_soil=inputs_hourly.psi_soil,
            t_soil=inputs_hourly.soil_temperature, t_sky_eff=inputs_hourly.sky_temperature, params=params,
            calc_collar_water_potential=calc_collar_water_potential)

        # Write mtg to an external file
        if is_save_mtg and (scene is not None):
            architecture.save_mtg(g=g, scene=scene, file_path=inputs.path_output_dir)

        # Plot stuff..
        sapflow.append(g.node(g.node(g.root).vid_collar).Flux)
        # sapEast.append(g.node(arm_vid['arm1']).Flux)
        # sapWest.append(g.node(arm_vid['arm2']).Flux)

        # Trace intercepted irradiance on each time step
        rg_ls.append(
            sum([g.node(vid).Ei / (0.48 * 4.6) * surface(g.node(vid).geometry) * (params.simulation.conv_to_meter ** 2)
                 for vid in g.property('geometry') if g.node(vid).label.startswith('L')]))

        an_ls.append(g.node(g.node(g.root).vid_collar).FluxC)

        psi_soil_ls.append(inputs_hourly.psi_soil)
        psi_collar_ls.append(g.node(g.node(g.root).vid_collar).psi_head)
        psi_leaf_ls.append(np.median([g.node(vid).psi_head for vid in g.property("gs").keys()]))

        leaf_temperature_dict[date] = deepcopy(g.property('Tlc'))

        print('---------------------------')
        print(f'psi_soil {inputs_hourly.psi_soil:.4f}')
        print(f'psi_collar {g.node(g.node(g.root).vid_collar).psi_head:.4f}')
        print(f'psi_leaf {np.median([g.node(vid).psi_head for vid in g.property("gs").keys()]):.4f}')
        print('')
        # print('Rdiff/Rglob ', RdRsH_ratio)
        # print('t_sky_eff ', t_sky_eff)
        print(f'gs: {np.median(list(g.property("gs").values())):.4f}')
        print(f'flux H2O {g.node(g.node(g.root).vid_collar).Flux * 1000. * time_conv:.4f}')
        print(f'flux C2O {g.node(g.node(g.root).vid_collar).FluxC}')
        print(f'Tleaf {np.median([g.node(vid).Tlc for vid in g.property("gs").keys()]):.2f}', ' ',
              f'Tair {inputs_hourly.weather.loc[date, "Tac"]:.2f}')
        print('')
        print(f'irrigation: {irrigation_rate}')
        print('')
        print("=" * 72)

    # End time loop +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Write output
    # Plant total transpiration
    sapflow = [flow * time_conv * 1000. for flow in sapflow]

    # sapEast, sapWest = [np.array(flow) * time_conv * 1000. for i, flow in enumerate((sapEast, sapWest))]

    # Median leaf temperature
    t_ls = [np.median(list(leaf_temperature_dict[date].values())) for date in params.simulation.date_range]

    # Intercepted global radiation
    rg_ls = np.array(rg_ls) / (params.planting.spacing_on_row * params.planting.spacing_between_rows)

    # Results DataFrame
    results_df = DataFrame({
        'Rg': rg_ls,
        'An': an_ls,
        'E': sapflow,
        # 'sapEast': sapEast,
        # 'sapWest': sapWest,
        'Tleaf': t_ls,
        'irr': irrigation_ls,
        'psi_soil': psi_soil_ls,
        'psi_collar': psi_collar_ls,
        'psi_leaf': psi_leaf_ls},
        index=params.simulation.date_range)

    # Write
    if write_result:
        results_df.to_csv(inputs.path_output_file, sep=';', decimal='.')

    time_off = datetime.now()

    print("")
    print("beg time", time_on)
    print("end time", time_off)
    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")
    return results_df
