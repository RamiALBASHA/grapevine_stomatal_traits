"""This is an example on running HydroShoot on a potted grapevine with a
simple shoot architecture.
"""

from pathlib import Path

from hydroshoot import architecture, display
from openalea.mtg import traversal, mtg
from openalea.plantgl.all import Scene

from grapevine_stomatal_traits.sims.preprocess_functions import preprocess_inputs


def build_mtg(path_file: Path, is_show_scene: bool = True) -> (mtg.MTG, Scene):
    grapevine_mtg = architecture.vine_mtg(file_path=path_file)

    for v in traversal.iter_mtg2(grapevine_mtg, grapevine_mtg.root):
        architecture.vine_phyto_modular(grapevine_mtg, v)
        architecture.vine_mtg_properties(grapevine_mtg, v)
        architecture.vine_mtg_geometry(grapevine_mtg, v)
        architecture.vine_transform(grapevine_mtg, v)

    # Display of the plant mock-up (result in 'fig_01_plant_mock_up.png')
    mtg_scene = display.visu(grapevine_mtg, def_elmnt_color_dict=True, scene=Scene(), view_result=is_show_scene)
    return grapevine_mtg, mtg_scene


if __name__ == '__main__':
    path_project = Path(__file__).parent
    path_preprocessed_data = path_project / 'preprocessed_inputs'

    g, scene = build_mtg(path_file=path_project / 'digit.csv', is_show_scene=False)
    preprocess_inputs(grapevine_mtg=g, path_project_dir=path_project, psi_soil=-0.5, gdd_since_budbreak=1000.,
                      scene=scene)
