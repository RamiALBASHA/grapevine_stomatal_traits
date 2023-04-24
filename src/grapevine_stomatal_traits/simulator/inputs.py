from datetime import datetime

from hydroshoot.display import visu
from hydroshoot.energy import force_soil_temperature
from hydroshoot.params import Params
from hydroshoot.soil import update_soil_water_potential
from openalea.mtg.mtg import MTG
from openalea.plantgl.all import Scene
from pandas import DataFrame


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
                self.psi_soil = update_soil_water_potential(
                    psi_soil_init=self.psi_soil,
                    water_withdrawal=(
                            (g.node(g.node(g.root).vid_collar).Flux * params.simulation.conv_to_second) - water_input),
                    soil_class=params.soil.soil_class,
                    soil_total_volume=params.soil.soil_volume,
                    psi_min=params.hydraulic.psi_min)

        pass
