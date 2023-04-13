from datetime import datetime
from enum import Enum

from grapevine_stomatal_traits.sources.config import SiteData, PhenoData


class SiteDataOakville(SiteData):
    def __init__(self, pheno_data: PhenoData):
        super(SiteDataOakville, self).__init__(
            pheno_data=pheno_data,
            latitude=38.43,
            longitude=-122.41,
            elevation=58,
            training_system='vsp',
            soil_class='Clay_Loam',
            spacing_interrow=1.8,
            spacing_intrarow=1.8,
            soil_depth=2.,
            rhyzo_coeff=0.75,
            root_radius=0.001,
            root_length=200,
            initial_soil_water_potential=-0.6)


ScenariosDatesOakville = [
    ('historical', PhenoData(
        date_budburst=datetime(1990, 4, 1),
        date_veraison=datetime(1990, 7, 30),
        gdd_since_budbreak=96)),
    ('rcp45', PhenoData(
        date_budburst=datetime(1990, 3, 8),
        date_veraison=datetime(1990, 7, 2),
        gdd_since_budbreak=96)),
    ('rcp85', PhenoData(
        date_budburst=datetime(1990, 2, 15),
        date_veraison=datetime(1990, 6, 11),
        gdd_since_budbreak=99))]
