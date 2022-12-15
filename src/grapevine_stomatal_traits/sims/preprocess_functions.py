from json import dump, load
from pathlib import Path

from hydroshoot import io, initialisation
from hydroshoot.architecture import vine_orientation
from openalea.mtg import mtg
from openalea.plantgl.scenegraph import Scene

from grapevine_stomatal_traits.sources.config import SiteData
from grapevine_stomatal_traits.sources.mockups.main_mockups import build_mtg

PATH_PARAMS_BASE = Path(__file__).parent / 'params_base.json'


def preprocess_inputs(grapevine_mtg: mtg.MTG, path_project_dir: Path, path_preprocessed_inputs_dir: Path,
                      psi_soil: float, scene: Scene, is_write_hourly_dynamic: bool = False, **kwargs):
    path_preprocessed_inputs_dir.mkdir(parents=True, exist_ok=True)

    inputs = io.HydroShootInputs(
        g=grapevine_mtg, path_project=path_project_dir, scene=scene, psi_soil=psi_soil, **kwargs)
    io.verify_inputs(g=grapevine_mtg, inputs=inputs)
    grapevine_mtg = initialisation.init_model(g=grapevine_mtg, inputs=inputs)

    static_data = {'form_factors': {s: grapevine_mtg.property(s) for s in ('ff_sky', 'ff_leaves', 'ff_soil')}}
    static_data.update({'Na': grapevine_mtg.property('Na')})

    with open(path_preprocessed_inputs_dir / 'static.json', mode='w') as f:
        dump(static_data, f, indent=2)

    dynamic_data = {}
    inputs_hourly = io.HydroShootHourlyInputs(psi_soil=inputs.psi_soil_forced, sun2scene=inputs.sun2scene)
    for date_sim in inputs.params.simulation.date_range:
        print(date_sim)
        inputs_hourly.update(
            g=grapevine_mtg, date_sim=date_sim, hourly_weather=inputs.weather[inputs.weather.index == date_sim],
            psi_pd=inputs.psi_pd, params=inputs.params)

        grapevine_mtg, diffuse_to_total_irradiance_ratio = initialisation.init_hourly(
            g=grapevine_mtg, inputs_hourly=inputs_hourly, leaf_ppfd=inputs.leaf_ppfd,
            params=inputs.params)

        dynamic_data_per_date = {
            'diffuse_to_total_irradiance_ratio': diffuse_to_total_irradiance_ratio,
            'Ei': grapevine_mtg.property('Ei'),
            'Eabs': grapevine_mtg.property('Eabs')}

        if is_write_hourly_dynamic:
            with open(path_preprocessed_inputs_dir / f'dynamic_{grapevine_mtg.date}.json', mode='w') as f:
                dump(dynamic_data_per_date, f, indent=2)

        dynamic_data.update({grapevine_mtg.date: dynamic_data_per_date})

    with open(path_preprocessed_inputs_dir / f'dynamic.json', mode='w') as f:
        dump(dynamic_data, f, indent=2)


def prepare_params(site_data: SiteData, stomatal_params: dict, scene_rotation: float, weather_file: str) -> dict:
    with open(PATH_PARAMS_BASE, mode='r') as f:
        params = load(f)
    params['simulation'].update({
        "sdate": site_data.date_start_sim,
        "edate": site_data.date_end_sim,
        "latitude": site_data.latitude,
        "longitude": site_data.longitude,
        "elevation": site_data.elevation,
        "meteo": weather_file})
    params['irradiance'].update({'scene_rotation': scene_rotation})
    params['phenology'].update({'emdate': site_data.date_budburst})
    params['exchange']['par_gs'].update(stomatal_params)
    params['soil'].update({
        'soil_class': site_data.soil_class,
        'soil_dimensions': [site_data.spacing_interrow,
                            site_data.spacing_intrarow,
                            site_data.soil_depth],
        'rhyzo_coeff': site_data.rhyzo_coeff})
    return params


def prepare_mtg(path_digit: Path, training_system: str, rotation_angle: float, is_leaf_follow_cordon: bool = True):
    g = build_mtg(
        path_csv=path_digit,
        training_system_name=training_system,
        is_cordon_preferential_orientation=is_leaf_follow_cordon)
    for v in mtg.traversal.iter_mtg2(g, g.root):
        vine_orientation(g, v, rotation_angle, local_rotation=False)
    return g
