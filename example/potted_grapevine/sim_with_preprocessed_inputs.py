"""This is an example on running HydroShoot on a potted grapevine with a
simple shoot architecture.
"""

from json import dump
from pathlib import Path

from hydroshoot import io, initialisation
from openalea.mtg.mtg import MTG
from openalea.plantgl.all import Scene

from example.potted_grapevine.sim import build_mtg


def preprocess_inputs(grapevine_mtg: MTG, path_project_dir: Path, psi_soil: float, gdd_since_budbreak: float,
                      scene: Scene):
    inputs = io.HydroShootInputs(g=grapevine_mtg, path_project=path_project_dir, scene=scene, psi_soil=psi_soil,
                                 gdd_since_budbreak=gdd_since_budbreak)
    io.verify_inputs(g=grapevine_mtg, inputs=inputs)
    grapevine_mtg = initialisation.init_model(g=grapevine_mtg, inputs=inputs)

    static_data = {'form_factors': {s: grapevine_mtg.property(s) for s in ('ff_sky', 'ff_leaves', 'ff_soil')}}
    static_data.update({'Na': grapevine_mtg.property('Na')})

    dynamic_data = {}
    inputs_hourly = io.HydroShootHourlyInputs(psi_soil=inputs.psi_soil_forced, sun2scene=inputs.sun2scene)
    for date_sim in inputs.params.simulation.date_range:
        print(date_sim)
        inputs_hourly.update(
            g=grapevine_mtg, date_sim=date_sim, hourly_weather=inputs.weather[inputs.weather.index == date_sim],
            psi_pd=inputs.psi_pd, params=inputs.params)

        grapevine_mtg, diffuse_to_total_irradiance_ratio = initialisation.init_hourly(
            g=grapevine_mtg, inputs_hourly=inputs_hourly, leaf_ppfd=inputs.leaf_ppfd,
            params=inputs.params)

        dynamic_data.update({grapevine_mtg.date: {
            'diffuse_to_total_irradiance_ratio': diffuse_to_total_irradiance_ratio,
            'Ei': grapevine_mtg.property('Ei'),
            'Eabs': grapevine_mtg.property('Eabs')}})

    path_preprocessed_inputs = path_project_dir / 'preprocessed_inputs'
    path_preprocessed_inputs.mkdir(parents=True, exist_ok=True)
    for s, data in (('static.json', static_data), ('dynamic.json', dynamic_data)):
        path_output = path_preprocessed_inputs / s
        with open(path_output, mode='w') as f_prop:
            dump(static_data, f_prop)


if __name__ == '__main__':
    path_project = Path(__file__).parent
    path_preprocessed_data = path_project / 'preprocessed_inputs'

    g, scene = build_mtg(path_file=path_project / 'digit.csv', is_show_scene=False)
    preprocess_inputs(grapevine_mtg=g, path_project_dir=path_project, psi_soil=-0.5, gdd_since_budbreak=1000.,
                      scene=scene)
