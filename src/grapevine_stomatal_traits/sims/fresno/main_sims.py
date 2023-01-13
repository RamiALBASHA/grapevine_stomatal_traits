from datetime import datetime
from pathlib import Path

from grapevine_stomatal_traits.sims.fresno.config import ScenariosDatesFresno
from grapevine_stomatal_traits.sims.sim_functions import run_simulations
from grapevine_stomatal_traits.sources.config import ScenariosRowAngle

if __name__ == '__main__':
    time_on = datetime.now()

    run_simulations(
        path_root=Path(__file__).parent.resolve(),
        scenario_dates=ScenariosDatesFresno,
        scenarios_row_angle=ScenariosRowAngle)

    time_off = datetime.now()
    print(f"--- Total runtime: {(time_off - time_on).seconds} sec ---")
