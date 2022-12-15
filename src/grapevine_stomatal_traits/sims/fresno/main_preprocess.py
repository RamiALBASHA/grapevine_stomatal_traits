from datetime import datetime
from json import dump
from pathlib import Path

from hydroshoot.display import visu
from openalea.plantgl.all import Scene

from grapevine_stomatal_traits.sims.fresno.config import SiteDataFresno
from grapevine_stomatal_traits.sims.preprocess_functions import prepare_params, preprocess_inputs, prepare_mtg
from grapevine_stomatal_traits.sources.config import ScenariosTraits


def set_params(path_project_dir: Path, rotation_angle: float, weather_file: str):
    params = prepare_params(
        site_data=SiteDataFresno(), stomatal_params=ScenariosTraits.baseline.value, scene_rotation=rotation_angle,
        weather_file=weather_file)
    with open(path_project_dir / 'params.json', mode='w') as f:
        dump(params, f, indent=2)
    pass


if __name__ == '__main__':
    time_on = datetime.now()
    path_root = Path(__file__).parent.resolve()
    # for weather_scenario in ('historical', 'rcp45', 'rcp85'):
    for weather_scenario in ('historical', ):
        print('-' * 30)
        print(f'weather scenario: {weather_scenario}')
        # for row_orientation, row_angle in (('northsouth', 0.), ('northeast_southwest', 45.), ('east_west', 90.)):
        for row_orientation, row_angle in (('northsouth', 0.), ):
            print(f'row orientation: {row_orientation}')
            set_params(
                path_project_dir=path_root,
                rotation_angle=row_angle,
                weather_file=f'weather_fresno_{weather_scenario}.csv')
            grapevine_mtg = prepare_mtg(
                path_digit=path_root.parents[1] / 'sources/mockups/sprawl/virtual_digit.csv',
                training_system='sprawl',
                rotation_angle=row_angle)
            scene = visu(grapevine_mtg, def_elmnt_color_dict=True, scene=Scene(), view_result=False)
            preprocess_inputs(
                grapevine_mtg=grapevine_mtg,
                path_project_dir=path_root,
                path_preprocessed_inputs_dir=path_root / 'preprocessed_inputs' / weather_scenario / row_orientation,
                gdd_since_budbreak=1000., psi_soil=0, scene=scene,
                is_write_hourly_dynamic=True)

    time_off = datetime.now()
    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")
