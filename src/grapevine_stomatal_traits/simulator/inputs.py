from datetime import datetime

import hydroshoot.constants as cst
from hydroshoot.display import visu
from hydroshoot.energy import force_soil_temperature
from hydroshoot.hydraulic import def_param_soil
from hydroshoot.params import Params
from numpy import array
from openalea.mtg.mtg import MTG
from openalea.plantgl.all import Scene
from pandas import DataFrame
from scipy import optimize


class HydroShootHourlyInputs(object):
    def __init__(self, psi_soil: float, sun2scene: Scene, is_psi_soil_forced: bool = False):
        self.date = None
        self.weather = None
        self.psi_soil = psi_soil
        self.sun2scene = sun2scene
        self.soil_temperature = None
        self.sky_temperature = None
        self.is_psi_soil_forced = is_psi_soil_forced

    def update(self, g: MTG, date_sim: datetime, hourly_weather: DataFrame, psi_pd: DataFrame, params: Params,
               water_input: float = None):
        self.date = date_sim
        self.weather = hourly_weather
        self.calc_psi_soil(g=g, water_input=water_input, psi_pd=psi_pd, params=params)
        self.sun2scene = visu(g, def_elmnt_color_dict=True, scene=Scene()) if self.sun2scene is not None else None
        self.soil_temperature = force_soil_temperature(self.weather)

        pass

    def calc_psi_soil(self, g: MTG, water_input: float, psi_pd: DataFrame, params: Params):
        if not self.is_psi_soil_forced:
            if self.date.hour == 0:
                try:
                    self.psi_soil = psi_pd.loc[self.date, :][0]
                except KeyError:
                    pass
            # Estimate soil water potential evolution due to transpiration
            else:
                self.psi_soil = soil_water_potential(
                    psi_soil_init=self.psi_soil,
                    water_withdrawal=0,  # water withdrawal will be considered later in the solver
                    water_input=water_input,
                    soil_class=params.soil.soil_class,
                    soil_total_volume=params.soil.soil_total_volume,
                    psi_min=params.hydraulic.psi_min)

        pass


def soil_water_potential(psi_soil_init, water_withdrawal, water_input, soil_class, soil_total_volume, psi_min=-3.):
    """Computes soil water potential following van Genuchten (1980)

    Args:
        psi_soil_init (float): [MPa] initial soil water potential
        water_withdrawal (float): [Kg T-1] water volume that is withdrawn from the soil (by transpiration for instance)
            during a timelapse T
        water_input (float): [Kg T-1] water volume that is added to the soil during a timelapse T
        soil_class (str): one of the soil classes proposed by Carsel and Parrish (1988), see :func:`def_param_soil` for
            details
        soil_total_volume (float): [m3] total apparent volume of the soil (including solid, liquid and gaseous
            fractions)
        psi_min (float): [MPa] minimum allowable water potential

    Returns:
        (float): [MPa] soil water potential

    Notes:
        Strictly speaking, :arg:`psi_min` expresses rather the minimum water potential at the base of the plant shoot.

    References:
        van Genuchten M., 1980.
            A closed-form equation for predicting the hydraulic conductivity of unsaturated soils.
            Soil Science Society of America Journal 44, 892897.
    """

    psi_soil_init = min(-1e-6, psi_soil_init)
    theta_r, theta_s, alpha, n, k_sat = def_param_soil()[soil_class]

    m = 1. - 1. / n

    psi = psi_soil_init * 1.e6 / (cst.water_density * cst.gravitational_acceleration) * 100.  # MPa -> cm_H20
    theta_init = theta_r + (theta_s - theta_r) / (1. + abs(alpha * psi) ** n) ** m

    flux = (water_withdrawal - water_input) * 1.e-3  # kg T-1 -> m3 T-1

    porosity_volume = soil_total_volume * theta_s

    delta_theta = flux / porosity_volume  # [m3 m-3]

    theta = max(theta_r, theta_init - delta_theta)

    if theta <= theta_r:
        psi_soil = psi_min
    elif theta >= theta_s:
        psi_soil = 0.0
    else:
        def _water_retention(x):
            return 1. / (1. + abs(alpha * x) ** n) ** m - (theta - theta_r) / (theta_s - theta_r)

        psi_soil = optimize.fsolve(_water_retention, array(psi))[0] / (
                1.e6 / (cst.water_density * cst.gravitational_acceleration) * 100)

    return max(psi_min, float(psi_soil))
