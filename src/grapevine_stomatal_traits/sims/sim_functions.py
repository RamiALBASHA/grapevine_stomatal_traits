from json import load
from pathlib import Path

from hydroshoot.architecture import load_mtg
from openalea.mtg.mtg import MTG
from openalea.plantgl.scenegraph import Scene

from grapevine_stomatal_traits.simulator import hydroshoot_wrapper
from grapevine_stomatal_traits.sources.config import ScenariosRowAngle


def _run_simulations(g: MTG, scene: Scene, path_root: Path, path_preprocessed_dir: Path,
                     row_angle_scenario: ScenariosRowAngle, climate_scenario: list):
    path_output = path_root / 'output' / climate_scenario[0] / row_angle_scenario.name
    path_output.mkdir(exist_ok=True, parents=True)

    with open(path_preprocessed_dir / 'static.json') as f:
        static_inputs = load(f)
    with open(path_preprocessed_dir / 'dynamic.json') as f:
        dynamic_inputs = load(f)

    hydroshoot_wrapper.run(
        g=g,
        wd=path_preprocessed_dir,
        scene=scene,
        path_output=path_output / 'time_series.csv',
        gdd_since_budbreak=climate_scenario[1].gdd_since_budbreak,
        form_factors=static_inputs['form_factors'],
        leaf_nitrogen=static_inputs['Na'],
        leaf_ppfd=dynamic_inputs,
        psi_soil_init=-0.01,
        drip_rate=3.8,
        replacement_fraction=0.6,
        irrigation_freq=2)

    pass


def run_simulations(path_root: Path, scenario_dates: list, scenario_angle: ScenariosRowAngle):
    print('-' * 30)
    print(f'climate scenario: {scenario_dates[0]}\nrow orientation: {scenario_angle.name}')

    path_preprocessed_dir = path_root / 'preprocessed_inputs' / scenario_dates[0] / scenario_angle.name

    g, scene = load_mtg(
        path_mtg=str(path_preprocessed_dir / 'initial_mtg.pckl'),
        path_geometry=str(path_preprocessed_dir / 'geometry.bgeom'))

    _run_simulations(
        g=g,
        scene=scene,
        path_root=path_root,
        path_preprocessed_dir=path_root / 'preprocessed_inputs' / scenario_dates[0] / scenario_angle.name,
        row_angle_scenario=scenario_angle,
        climate_scenario=scenario_dates)

    pass
