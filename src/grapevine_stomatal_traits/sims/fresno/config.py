from datetime import datetime
from enum import Enum

from grapevine_stomatal_traits.sources.config import SiteData, PhenoData


class SiteDataFresno(SiteData):
    def __init__(self, pheno_data: PhenoData):
        super(SiteDataFresno, self).__init__(
            pheno_data=pheno_data,
            latitude=36.82,
            longitude=-119.74,
            elevation=104,
            training_system='sprawl',
            soil_class='Clay_Loam',
            spacing_interrow=1.8,
            spacing_intrarow=2.2,
            soil_depth=2.,
            rhyzo_coeff=0.75)


ScenariosDatesFresno = [
    ('historical', PhenoData(
        date_budburst=datetime(1990, 3, 25),
        date_veraison=datetime(1990, 7, 15),
        gdd_since_budbreak=98)),
    ('rcp45', PhenoData(
        date_budburst=datetime(1990, 2, 27),
        date_veraison=datetime(1990, 6, 20),
        gdd_since_budbreak=99)),
    ('rcp85', PhenoData(
        date_budburst=datetime(1990, 2, 7),
        date_veraison=datetime(1990, 6, 6),
        gdd_since_budbreak=99))]
