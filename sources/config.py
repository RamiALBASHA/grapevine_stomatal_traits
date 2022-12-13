from enum import Enum


class SiteData(object):
    def __init__(self, date_start_sim: str, date_end_sim: str, date_budburst: str, latitude: float, longitude: float,
                 elevation: float, soil_class: str, spacing_interrow: float, spacing_intrarow: float, soil_depth: float,
                 rhyzo_coeff: float):
        self.date_start_sim = date_start_sim
        self.date_end_sim = date_end_sim
        self.date_budburst = date_budburst
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.soil_class = soil_class
        self.spacing_interrow = spacing_interrow
        self.spacing_intrarow = spacing_intrarow
        self.soil_depth = soil_depth
        self.rhyzo_coeff = rhyzo_coeff


class ScenariosTraits(Enum):
    baseline: dict = {"g0": 0.01145, 'm0': 5.06, 'psi0': -1.27}
    low_gmax: dict = {"g0": 0.01145, 'm0': 1.72, 'psi0': -1.27}
    high_gmax: dict = {"g0": 0.01145, 'm0': 7.04, 'psi0': -1.27}
    high_gsp50: dict = {"g0": 0.01145, 'm0': 5.06, 'psi0': 0.93}
    low_gsp50: dict = {"g0": 0.01145, 'm0': 5.06, 'psi0': -1.54}
    elite: dict = {"g0": 0.01165, 'm0': 0.8925, 'psi0': -0.85}


class ScenariosField(Enum):
    scene_rotation: list = [0., 45., 90.]
