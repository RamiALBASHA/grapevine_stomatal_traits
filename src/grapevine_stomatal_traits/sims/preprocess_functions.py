from json import dump, load
from pathlib import Path

from hydroshoot import io, initialisation
from hydroshoot.architecture import vine_orientation, mtg_save_geometry, save_mtg
from hydroshoot.display import visu
from openalea.mtg import mtg
from openalea.plantgl.scenegraph import Scene

from grapevine_stomatal_traits.sources.config import SiteData
from grapevine_stomatal_traits.sources.mockups.main_mockups import build_mtg

PATH_PARAMS_BASE = Path(__file__).parent / 'params_base.json'

FMT_DATES = '%Y-%m-%d %H:%M:%S'


def preprocess_inputs(grapevine_mtg: mtg.MTG, path_project_dir: Path, path_preprocessed_inputs_dir: Path,
                      path_weather: Path, psi_soil: float, scene: Scene, is_write_hourly_dynamic: bool = False,
                      **kwargs):
    path_preprocessed_inputs_dir.mkdir(parents=True, exist_ok=True)

    inputs = io.HydroShootInputs(
        path_project=path_project_dir,
        path_weather=path_weather,
        scene=scene,
        user_params=None,
        psi_soil=psi_soil,
        **kwargs)

    io.verify_inputs(g=grapevine_mtg, inputs=inputs)
    grapevine_mtg = initialisation.init_model(g=grapevine_mtg, inputs=inputs)

    static_data = {'form_factors': {s: grapevine_mtg.property(s) for s in ('ff_sky', 'ff_leaves', 'ff_soil')}}
    static_data.update({'Na': grapevine_mtg.property('Na')})

    with open(path_preprocessed_inputs_dir / 'static.json', mode='w') as f:
        dump(static_data, f, indent=2)

    save_mtg(g=grapevine_mtg, scene=scene, file_path=path_preprocessed_inputs_dir, filename='initial_mtg.pckl')

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


def prepare_params(site_data: SiteData, stomatal_params: dict, scene_rotation: float) -> dict:
    with open(PATH_PARAMS_BASE, mode='r') as f:
        params = load(f)
    params['simulation'].update({
        "sdate": site_data.date_start_sim.strftime(FMT_DATES),
        "edate": site_data.date_end_sim.strftime(FMT_DATES),
        "latitude": site_data.latitude,
        "longitude": site_data.longitude,
        "elevation": site_data.elevation})
    params['planting'].update({
        'spacing_between_rows': site_data.spacing_interrow,
        'spacing_on_row': site_data.spacing_intrarow,
        'row_angle_with_south': scene_rotation})
    params['phenology'].update({'emdate': site_data.date_budburst.strftime(FMT_DATES)})
    params['exchange']['par_gs'].update(stomatal_params)
    params['soil'].update({
        'soil_class': site_data.soil_class,
        'soil_dimensions': {
            'depth': site_data.soil_depth},
        'rhyzo_coeff': site_data.rhyzo_coeff,
        'avg_root_radius': site_data.avg_root_radius,
        'root_length': site_data.root_length})
    return params


def set_params(path_project_dir: Path, site_data: SiteData, stomatal_params: dict, rotation_angle: float):
    params = prepare_params(site_data=site_data, stomatal_params=stomatal_params, scene_rotation=rotation_angle)
    with open(path_project_dir / 'params.json', mode='w') as f:
        dump(params, f, indent=2)
    pass


def set_initial_predawn_soil_water_potential(path_project_dir: Path, site_data: SiteData):
    with(open(path_project_dir / 'psi_soil.input', mode='w')) as f:
        f.write('time;psi\n')
        f.write(f"{site_data.date_start_sim.strftime('%Y-%m-%d')};{site_data.initial_soil_water_potential}")
    pass


def prepare_mtg(path_digit: Path, training_system: str, rotation_angle: float, is_leaf_follow_cordon: bool = True):
    g = build_mtg(
        path_csv=path_digit,
        training_system_name=training_system,
        is_cordon_preferential_orientation=is_leaf_follow_cordon)
    for v in mtg.traversal.iter_mtg2(g, g.root):
        vine_orientation(g, v, rotation_angle, local_rotation=False)
    return g


def preprocess_inputs_and_params(path_root: Path, path_preprocessed_dir: Path,
                                 site_data: SiteData, weather_file_name: str,
                                 stomatal_params: dict, row_angle_from_south: float):
    training_system = site_data.training_system
    path_digit = path_root.parents[1] / f'sources/mockups/{training_system}/virtual_digit.csv'

    path_preprocessed_dir.mkdir(parents=True, exist_ok=True)

    set_params(
        path_project_dir=path_preprocessed_dir,
        site_data=site_data,
        stomatal_params=stomatal_params,
        rotation_angle=row_angle_from_south)
    set_initial_predawn_soil_water_potential(
        path_project_dir=path_preprocessed_dir,
        site_data=site_data)
    grapevine_mtg = prepare_mtg(
        path_digit=path_digit,
        training_system=training_system,
        rotation_angle=row_angle_from_south)
    scene = visu(grapevine_mtg, def_elmnt_color_dict=True, scene=Scene(), view_result=False)
    mtg_save_geometry(scene=scene, file_path=path_preprocessed_dir)

    preprocess_inputs(
        grapevine_mtg=grapevine_mtg,
        path_project_dir=path_preprocessed_dir,
        path_preprocessed_inputs_dir=path_preprocessed_dir,
        path_weather=path_root / weather_file_name,
        gdd_since_budbreak=site_data.gdd_since_budbreak,
        psi_soil=0,
        scene=scene,
        is_write_hourly_dynamic=True)
