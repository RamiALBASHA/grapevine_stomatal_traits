from datetime import datetime
from enum import Enum

from dateutil.relativedelta import relativedelta


class PhenoData:
    def __init__(self, date_budburst: datetime, date_veraison: datetime, gdd_since_budbreak: float):
        self.date_budbreak = date_budburst
        self.date_start_sim = date_veraison
        self.date_end_sim = date_veraison + relativedelta(months=+1, days=-1)
        self.gdd_since_budbreak = gdd_since_budbreak


class SiteData(object):
    def __init__(self, pheno_data: PhenoData, latitude: float, longitude: float,
                 elevation: float, training_system: str, soil_class: str, spacing_interrow: float,
                 spacing_intrarow: float, soil_depth: float, rhyzo_coeff: float, initial_soil_water_potential: float):
        self.date_budburst = pheno_data.date_budbreak
        self.date_start_sim = pheno_data.date_start_sim
        self.date_end_sim = pheno_data.date_end_sim
        self.gdd_since_budbreak = pheno_data.gdd_since_budbreak
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.training_system = training_system
        self.soil_class = soil_class
        self.spacing_interrow = spacing_interrow
        self.spacing_intrarow = spacing_intrarow
        self.soil_depth = soil_depth
        self.rhyzo_coeff = rhyzo_coeff
        self. initial_soil_water_potential = initial_soil_water_potential


class ScenariosTraits(Enum):
    baseline: dict = {"g0": 0.01145, 'm0': 5.06, 'psi0': -1.27}
    low_gmax: dict = {"g0": 0.01145, 'm0': 1.72, 'psi0': -1.27}
    high_gmax: dict = {"g0": 0.01145, 'm0': 7.04, 'psi0': -1.27}
    high_gsp50: dict = {"g0": 0.01145, 'm0': 5.06, 'psi0': -0.93}
    low_gsp50: dict = {"g0": 0.01145, 'm0': 5.06, 'psi0': -1.54}
    elite: dict = {"g0": 0.01165, 'm0': 0.8925, 'psi0': -0.85}


class ScenariosRowAngle(Enum):
    north_south: float = 0.
    # northeast_southwest: float = 45.
    east_west: float = 90.
