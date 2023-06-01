"""This is an example on running HydroShoot on a potted grapevine with a
simple shoot architecture.
"""

from json import load
from pathlib import Path

from example.potted_grapevine.main_preprocess import build_mtg
from grapevine_stomatal_traits.simulator import hydroshoot_wrapper

if __name__ == '__main__':
    path_project = Path(__file__).parent
    path_preprocessed_data = path_project / 'preprocessed_inputs'

    g, scene = build_mtg(path_file=path_project / 'digit.csv', is_show_scene=False)

    with open(path_preprocessed_data / 'static.json') as f:
        static_inputs = load(f)
    with open(path_preprocessed_data / 'dynamic.json') as f:
        dynamic_inputs = load(f)
    with open(path_project / 'params.json', mode='r') as f:
        params = load(f)

    summary_results = hydroshoot_wrapper.run(
        g=g,
        wd=path_project,
        params=params,
        path_weather=path_project / 'weather.csv',
        scene=scene,
        path_output=path_project / 'output' / 'time_series_with_preprocessed_data.csv',
        gdd_since_budbreak=1000.,
        form_factors=static_inputs['form_factors'],
        leaf_nitrogen=static_inputs['Na'],
        leaf_ppfd=dynamic_inputs,
        # psi_soil_init=-0.5,
        drip_rate=3.8,
        replacement_fraction=0.6,
        irrigation_freq=2)
