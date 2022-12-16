from grapevine_stomatal_traits.sources.config import SiteData


class SiteDataFresno(SiteData):
    def __init__(self):
        super(SiteDataFresno, self).__init__(
            date_start_sim='1990-07-12 00:00:00',
            date_end_sim='1990-08-11 23:00:00',
            date_budburst='1990-04-01 00:00:00',
            latitude=36.82,
            longitude=-119.74,
            elevation=104,
            training_system='sprawl',
            soil_class='Clay_Loam',
            spacing_interrow=1.8,
            spacing_intrarow=2.2,
            soil_depth=2.,
            rhyzo_coeff=0.75)
