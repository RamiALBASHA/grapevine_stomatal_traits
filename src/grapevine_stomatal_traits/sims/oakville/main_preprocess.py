from datetime import datetime
from pathlib import Path

from grapevine_stomatal_traits.sims.oakville.config import SiteDataOakville, ScenariosDatesOakville
from grapevine_stomatal_traits.sims.preprocess_functions import preprocess_inputs_and_params
from grapevine_stomatal_traits.sources.config import ScenariosTraits, ScenariosRowAngle

if __name__ == '__main__':
    path_root = Path(__file__).parent.resolve()

    time_on = datetime.now()
    for scenario_climate in ScenariosDatesOakville:
        for row_angle_scenario in ScenariosRowAngle:
            print('-' * 30)
            print(f'climate scenario: {scenario_climate.name}\nrow orientation: {row_angle_scenario.name}')

            path_preprocessed_dir = path_root / 'preprocessed_inputs' / scenario_climate.name / row_angle_scenario.name
            path_preprocessed_dir.mkdir(parents=True, exist_ok=True)

            preprocess_inputs_and_params(
                path_root=path_root,
                path_preprocessed_dir=path_preprocessed_dir,
                site_data=SiteDataOakville(scenario_climate.value),
                weather_file_name=f'weather_{path_root.stem}_{scenario_climate.name}.csv',
                stomatal_params=ScenariosTraits.baseline.value,
                row_angle_from_south=row_angle_scenario.value)

    time_off = datetime.now()
    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")
