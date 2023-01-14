from datetime import datetime
from itertools import product
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable

from grapevine_stomatal_traits.sims.fresno.config import SiteDataFresno, ScenariosDatesFresno
from grapevine_stomatal_traits.sims.preprocess_functions import preprocess_inputs_and_params
from grapevine_stomatal_traits.sources.config import ScenariosTraits, ScenariosRowAngle


def _run_preprocesses(path_project: Path, scenario_dates: list, scenario_angle: ScenariosRowAngle):
    path_preprocessed_dir = path_project / 'preprocessed_inputs' / scenario_dates[0] / scenario_angle.name
    path_preprocessed_dir.mkdir(parents=True, exist_ok=True)

    preprocess_inputs_and_params(
        path_root=path_project,
        path_preprocessed_dir=path_preprocessed_dir,
        site_data=SiteDataFresno(scenario_dates[1]),
        weather_file_name=f'weather_{path_project.stem}_{scenario_dates[0]}.csv',
        stomatal_params=ScenariosTraits.baseline.value,
        row_angle_from_south=scenario_angle.value)


def run_preprocess(args):
    return _run_preprocesses(*args)


def mp(sim_args: Iterable, nb_cpu: int = 2):
    with Pool(nb_cpu) as p:
        p.map(run_preprocess, sim_args)


if __name__ == '__main__':
    path_root = Path(__file__).parent.resolve()

    time_on = datetime.now()
    mp(sim_args=product([path_root], ScenariosDatesFresno, ScenariosRowAngle), nb_cpu=4)
    time_off = datetime.now()
    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")
