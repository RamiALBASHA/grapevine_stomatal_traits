"""This is an example on running HydroShoot on a potted grapevine with a
simple shoot architecture.
"""

from json import load
from pathlib import Path

from hydroshoot import model

from example.potted_grapevine.main_preprocess import build_mtg

if __name__ == '__main__':
    path_project = Path(__file__).parent
    path_preprocessed_data = path_project / 'preprocessed_inputs'

    g, scene = build_mtg(path_file=path_project / 'grapevine_pot.csv', is_show_scene=False)

    with open(path_preprocessed_data / 'static.json') as f:
        static_inputs = load(f)
    with open(path_preprocessed_data / 'dynamic.json') as f:
        dynamic_inputs = load(f)

    summary_results = model.run(g=g, wd=path_project, scene=scene, psi_soil=-0.5, gdd_since_budbreak=1000.,
                                form_factors=static_inputs['form_factors'],
                                leaf_nitrogen=static_inputs['Na'],
                                leaf_ppfd=dynamic_inputs,
                                path_output=path_project / 'output' / 'time_series_with_preprocessed_data.csv')
