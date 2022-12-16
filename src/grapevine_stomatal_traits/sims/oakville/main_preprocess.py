from datetime import datetime
from pathlib import Path

from grapevine_stomatal_traits.sims.oakville.config import SiteDataOakville
from grapevine_stomatal_traits.sims.preprocess_functions import preprocess_inputs_and_params
from grapevine_stomatal_traits.sources.config import ScenariosTraits, ScenariosRowAngle

if __name__ == '__main__':
    time_on = datetime.now()
    path_root = Path(__file__).parent.resolve()

    for row_angle_scenario in ScenariosRowAngle:
        print('-' * 30)
        print(f'row orientation: {row_angle_scenario.name}')

        preprocess_inputs_and_params(
            path_root=path_root,
            site_data=SiteDataOakville(),
            weather_file_name=f'weather_{path_root.stem}_historical.csv',
            stomatal_params=ScenariosTraits.baseline.value,
            row_angle_scenario=row_angle_scenario,
            gdd_since_budbreak=1000.)

    time_off = datetime.now()
    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")
