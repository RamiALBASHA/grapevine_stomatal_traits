from datetime import datetime
from pathlib import Path

from grapevine_stomatal_traits.sims.fresno.config import SiteDataFresno
from grapevine_stomatal_traits.sims.preprocess_functions import preprocess_inputs_and_params
from grapevine_stomatal_traits.sources.config import ScenariosTraits

if __name__ == '__main__':
    time_on = datetime.now()
    path_root = Path(__file__).parent.resolve()

    for row_orientation, row_angle in (('northsouth', 0.), ('northeast_southwest', 45.), ('east_west', 90.)):
        print('-' * 30)
        print(f'row orientation: {row_orientation}')
        path_preprocessed_dir = path_root / 'preprocessed_inputs' / row_orientation
        path_preprocessed_dir.mkdir(parents=True, exist_ok=True)

        preprocess_inputs_and_params(
            path_digit=path_root.parents[1] / 'sources/mockups/sprawl/virtual_digit.csv',
            path_preprocessed_dir=path_preprocessed_dir,
            training_system='sprawl',
            site_data=SiteDataFresno(),
            weather_file_name='weather_fresno_historical.csv',
            stomatal_params=ScenariosTraits.baseline.value,
            row_angle_from_south=row_angle,
            gdd_since_budbreak=1000.)

    time_off = datetime.now()
    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")
