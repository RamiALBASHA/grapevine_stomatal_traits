from datetime import datetime
from itertools import product
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable

from grapevine_stomatal_traits.sims.fresno.config import ScenariosDatesFresno
from grapevine_stomatal_traits.sims.sim_functions import run_simulations
from grapevine_stomatal_traits.sources.config import ScenariosRowAngle, ScenariosTraits


def run_sims(args):
    return run_simulations(*args)


def mp(sim_args: Iterable, nb_cpu: int = 2):
    with Pool(nb_cpu) as p:
        p.map(run_sims, sim_args)


if __name__ == '__main__':
    time_on = datetime.now()
    mp(sim_args=product([Path(__file__).parent.resolve()], ScenariosDatesFresno, ScenariosRowAngle, ScenariosTraits),
       nb_cpu=12)
    time_off = datetime.now()
    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")
