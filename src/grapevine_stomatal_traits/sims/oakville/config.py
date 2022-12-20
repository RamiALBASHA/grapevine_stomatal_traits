from grapevine_stomatal_traits.sources.config import SiteData


class SiteDataOakville(SiteData):
    def __init__(self):
        super(SiteDataOakville, self).__init__(
            date_start_sim='1990-07-31 00:00:00',
            date_end_sim='1990-08-30 23:00:00',
            date_budburst='1990-04-01 00:00:00',
            latitude=38.43,
            longitude=-122.41,
            elevation=58,
            training_system='vsp',
            soil_class='Clay_Loam',
            spacing_interrow=1.8,
            spacing_intrarow=1.8,
            soil_depth=2.,
            rhyzo_coeff=0.75)
