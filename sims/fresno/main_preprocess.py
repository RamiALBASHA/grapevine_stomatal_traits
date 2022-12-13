from json import dump
from pathlib import Path

from hydroshoot.display import visu
from openalea.plantgl.all import Scene

from sims.fresno.config import SiteDataFresno
from sims.preprocess_functions import prepare_params, preprocess_inputs, prepare_mtg
from sources.config import ScenariosTraits


def set_params(path_project_dir: Path, rotation_angle: float, weather_file: str):
    params = prepare_params(
        site_data=SiteDataFresno(), stomatal_params=ScenariosTraits.baseline.value, scene_rotation=rotation_angle,
        weather_file=weather_file)
    with open(path_project_dir / 'params.json', mode='w') as f:
        dump(params, f, indent=2)
    pass


if __name__ == '__main__':
    path_root = Path(__file__).parent

    for weather_scenario in ('historical', 'rcp45', 'rcp85'):
        for row_orientation, row_angle in (('n_s', 0.), ('ne_sw', 45.), ('e_w', 90.)):
            set_params(
                path_project_dir=path_root,
                rotation_angle=row_angle,
                weather_file=f'weather_fresno_{weather_scenario}.csv')
            grapevine_mtg = prepare_mtg(
                path_digit=path_root.parents[1] / 'sources/mockups/sprawl/virtual_digit.csv',
                rotation_angle=row_angle)
            scene = visu(grapevine_mtg, def_elmnt_color_dict=True, scene=Scene(), view_result=False)
            preprocess_inputs(grapevine_mtg=grapevine_mtg, path_project_dir=path_root, psi_soil=0, scene=scene,
                              gdd_since_budbreak=1000.)
