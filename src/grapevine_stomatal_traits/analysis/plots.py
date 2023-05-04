from datetime import timedelta, datetime
from itertools import product
from pathlib import Path
from typing import Callable

import matplotlib.dates as mdates
from hydroshoot import constants
from matplotlib import pyplot
from pandas import DataFrame, read_csv, concat, merge

from grapevine_stomatal_traits.sims.fresno.config import ScenariosDatesFresno
from grapevine_stomatal_traits.sims.oakville.config import ScenariosDatesOakville

SITES = ('fresno', 'oakville')
SCEN_CLIM = ('historical', 'rcp45', 'rcp85')
# SCEN_ORIENT = ('north_south', 'northeast_southwest', 'east_west')
SCEN_ORIENT = ('north_south', 'east_west')
SCEN_TRAIT = ('baseline', 'low_gmax', 'high_gmax', 'high_gsp50', 'low_gsp50', 'elite')

MAP_UNITS = {
    "An": ("An", r"$\mathregular{(g\/h^{-1})}$"),
    "E": ("E", r"$\mathregular{(g\/h^{-1})}$"),
    "Tleaf": (r"$\mathregular{T_{leaf}}$", r"$\mathregular{(^\circ C)}$"),
    "wue": ("WUE", r"$\mathregular{(g_{CO_2(assimilated)}\/g_{H_2O}^{-1})}$"),
    "psi_soil": (r"$\mathregular{\Psi_{soil}}$", "(MPa)"),
    "psi_leaf": (r"$\mathregular{\Psi_{leaf}}$", "(MPa)"),
    "north_south": ('NS', ''),
    "east_west": ('EW', ''),
}


def get_unit(var_name: str) -> str:
    return " ".join(MAP_UNITS[var_name])


def calc_wue(data: DataFrame) -> float:
    return data['An'].sum() / data['E'].sum()


def get_all_time_series(path_time_series: Path, path_output: Path = None) -> DataFrame:
    combi = list(product(SITES, SCEN_CLIM, SCEN_ORIENT, SCEN_TRAIT))
    res = None
    for cmb in combi:
        path_file = path_time_series / '/'.join(cmb) / 'time_series.csv'
        if path_file.exists():
            df = read_csv(path_time_series / '/'.join(cmb) / 'time_series.csv', sep=';', decimal='.',
                          parse_dates=[0])
            df.drop(df.index.max(), inplace=True)
            df.loc[:, ['site', 'clim', 'orient', 'trait']] = list(zip(*[[v] * df.shape[0] for v in cmb]))

            if res is None:
                res = df
            else:
                res = concat([res, df])
    res.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
    # umol(CO2) s-1 -> g(CO2) h-1
    res.loc[:, 'An'] = res.apply(lambda x: x['An'] * 1.e-6 * constants.co2_molar_mass * 3600., axis=1)
    if path_output is not None:
        res.to_csv(path_output, decimal='.', sep=';')
    return res


def get_weather_data(path_sims: Path) -> DataFrame:
    res = None
    for cmb in list(product(SITES, SCEN_CLIM)):
        df = read_csv(path_sims / cmb[0] / f'weather_{cmb[0]}_{cmb[1]}.csv', sep=';', decimal='.', parse_dates=[0])
        df.loc[:, ['site', 'clim']] = list(zip(*[[v] * df.shape[0] for v in cmb]))
        if res is None:
            res = df
        else:
            res = concat([res, df])
    return res.sort_values('time')


def plot_trait_effect(data: DataFrame, path_fig: Path, is_relative: bool, var_name: str = 'wue') -> None:
    is_wue = var_name == 'wue'
    is_temperature = var_name == 'Tleaf'
    fig, axs = pyplot.subplots(nrows=len(SCEN_CLIM), ncols=len(SITES), sharex='all', sharey='all', figsize=(5, 5))

    for j, site in enumerate(SITES):
        for i, scen_clim in enumerate(SCEN_CLIM):
            ax = axs[i, j]
            if is_relative:
                ax.hlines(0 if is_temperature else 1, 0, 4, 'r')
                if i + j == 0:
                    xy_text = (0, 0.04) if is_temperature else (0, 1.04) if is_wue else (2.6, 1.03)
                    ax.text(*xy_text, 'baseline', color='r')

            for scen_orient in SCEN_ORIENT:
                df = data[(data['site'] == site) &
                          (data['clim'] == scen_clim) &
                          (data['orient'] == scen_orient)]
                if not df.empty:
                    if is_temperature:
                        gdf = df.groupby(by='trait').max(numeric_only=True)
                    else:
                        gdf = df.groupby(by='trait').sum(numeric_only=True)
                    gdf_var = (gdf['An'] / gdf['E']) if is_wue else gdf[var_name]
                    res = dict()
                    for s in SCEN_TRAIT:
                        try:
                            res[s] = gdf_var.loc[s]
                        except KeyError:
                            res[s] = None
                    lbl = {'north_south': 'NS', 'northeast_southwest': 'NE-SW', 'east_west': 'EW'}
                    if not is_relative:
                        x, y = zip(*[(s, res[s])
                                     for s in
                                     ('baseline', 'high_gmax', 'low_gsp50', 'low_gmax', 'high_gsp50', 'elite')])
                    else:
                        if is_temperature:
                            x, y = zip(*[(s, res[s] - res['baseline'])
                                         for s in ('high_gmax', 'low_gsp50', 'low_gmax', 'high_gsp50', 'elite')])
                        else:
                            x, y = zip(*[(s, res[s] / res['baseline'])
                                         for s in ('high_gmax', 'low_gsp50', 'low_gmax', 'high_gsp50', 'elite')])
                    ax.plot(x, y, marker='.', linestyle='-', label=lbl[scen_orient])

    for j, site in enumerate(SITES):
        axs[0, j].set_title(site.capitalize())
        axs[-1, j].set_xticks(x)
        axs[-1, j].set_xticklabels(x)
        axs[-1, j].tick_params(axis='x', labelrotation=90)
    for i, scen_clim in enumerate(SCEN_CLIM):
        axs[i, 0].set_ylabel({'historical': 'Historical', 'rcp45': 'RCP 4.5', 'rcp85': 'RCP 8.5'}[scen_clim])

    axs[0, 0].legend(fontsize=8)
    title_beg = 'relative ' if is_relative else ''
    title_unit = '(-)' if is_relative else MAP_UNITS[var_name][1]
    fig.suptitle(f"{title_beg}{var_name} {title_unit}")
    fig.tight_layout()
    fig.savefig(
        path_fig / f'trait_effect_{"wue" if var_name is None else var_name}{"relative" if is_relative else ""}.png')
    pass


def plot_water_potential(data: DataFrame, path_fig: Path) -> None:
    for site in SITES:
        fig, axs = pyplot.subplots(nrows=len(SCEN_CLIM), ncols=len(SCEN_TRAIT), sharex='all', sharey='all',
                                   figsize=(10, 5))

        for j, trait in enumerate(SCEN_TRAIT):
            for i, clim in enumerate(SCEN_CLIM):
                for orient in ('north_south',):
                    df = data[(data['site'] == site) &
                              (data['clim'] == clim) &
                              (data['orient'] == orient) &
                              (data['trait'] == trait)]
                    if not df.empty:
                        for v in ('psi_soil', 'psi_leaf'):
                            axs[i, j].plot(df.index.values, df[v], label=v.split("_")[1])

        for j, trait in enumerate(SCEN_TRAIT):
            axs[0, j].set_title(trait)
        for i, clim in enumerate(SCEN_CLIM):
            axs[i, 0].set_ylabel(clim)

        axs[-1, 2].set_xlabel('hour since veraison onset')
        axs[-1, 2].xaxis.set_label_coords(1.15, -.35, transform=axs[-1, 2].transAxes)
        axs[0, -1].legend()
        axs[0, 0].set_ylim(-3.1, 0)
        fig.suptitle(f'{site.capitalize()}: water potential (MPa)')
        fig.tight_layout()
        fig.savefig(path_fig / f'psi_{site}.png')
    pass


def plot_output(data: DataFrame, var_name: str, path_fig: Path) -> None:
    func = max if var_name == 'Tleaf' else sum if var_name in ('An', 'E') else None
    for site in SITES:
        fig, axs = pyplot.subplots(nrows=len(SCEN_CLIM), ncols=len(SCEN_TRAIT), sharex='row', sharey='all',
                                   figsize=(10, 5))

        for j, trait in enumerate(SCEN_TRAIT):
            for i, clim in enumerate(SCEN_CLIM):
                for orient in SCEN_ORIENT:
                    df = data[(data['site'] == site) &
                              (data['clim'] == clim) &
                              (data['orient'] == orient) &
                              (data['trait'] == trait)]
                    df.set_index('time', inplace=True)
                    if not df.empty:
                        if func is not None:
                            gdf = df.resample('D').aggregate(func)
                            axs[i, j].plot(gdf.index.day_of_year, gdf[var_name].values, label=get_unit(orient))
                            # gdf = df.groupby(df['time'].dt.date)[var_name].aggregate(func)
                            # axs[i, j].plot(range(gdf.index.shape[0]), gdf.values, label=get_unit(orient))
                        else:
                            axs[i, j].plot(df.index.values, df[var_name], label=var_name)

        for j, trait in enumerate(SCEN_TRAIT):
            axs[0, j].set_title(trait)
            axs[-1, j].set_xlabel('DOY')
        for i, clim in enumerate(SCEN_CLIM):
            axs[i, 0].set_ylabel(clim)

        if var_name in ('An', 'E'):
            axs[0, 0].set_ylim(0, {'An': 220, 'E': 41000}[var_name])

        axs[-1, -1].legend()
        fig.suptitle(f'{site.capitalize()}: {" ".join(MAP_UNITS[var_name])}')
        fig.tight_layout()
        fig.savefig(path_fig / f'{var_name}_{site}.png')
    pass


def plot_temperature(data: DataFrame, weather: DataFrame, path_fig: Path, func: Callable = None, is_dt: bool = False):
    for site in SITES:
        fig, axs = pyplot.subplots(nrows=len(SCEN_CLIM), ncols=len(SCEN_TRAIT), sharex='row', sharey='all',
                                   figsize=(10, 5))

        for j, trait in enumerate(SCEN_TRAIT):
            for i, clim in enumerate(SCEN_CLIM):
                w = weather[(weather['site'] == site) & (weather['clim'] == clim)]
                for orient in SCEN_ORIENT:
                    df = data[(data['site'] == site) &
                              (data['clim'] == clim) &
                              (data['orient'] == orient) &
                              (data['trait'] == trait)]
                    if not df.empty:
                        mdf = merge(left=df[['Tleaf', 'time']], right=w[['Tac', 'time']], how='inner').set_index('time')
                        gdf = mdf.resample('D').aggregate(max if func is None else func)
                        x = gdf.index.day_of_year
                        if is_dt:
                            axs[i, j].plot(x, gdf['Tleaf'] - gdf['Tac'], label=orient)
                        else:
                            axs[i, j].plot(x, gdf['Tleaf'], 'g-', label=orient)
                            axs[i, j].plot(x, gdf['Tac'], 'b-', label=orient)

        for j, trait in enumerate(SCEN_TRAIT):
            axs[0, j].set_title(trait)
            axs[-1, j].set_xlabel('DOY')
        for i, clim in enumerate(SCEN_CLIM):
            axs[i, 0].set_ylabel(clim)

        if not is_dt:
            axs[-1, -1].legend()
        else:
            axs[0, 0].set_ylim(-2, 0)
        fig.suptitle(f'{site.capitalize()}: max daily {"Tleaf-Tair" if is_dt else "Tleaf"}')
        fig.tight_layout()
        fig.savefig(path_fig / f'{"dTleaf" if is_dt else "Tleaf"}_{site}.png')
    pass


def plot_weather_conditions(weather: DataFrame, path_fig: Path):
    weather.set_index('time', inplace=True)
    fig, axs = pyplot.subplots(ncols=len(SCEN_CLIM), nrows=len(SITES), sharex='all', sharey='all')
    for j, clim in enumerate(SCEN_CLIM):
        axs[0, j].set_title(clim.capitalize())
        for i, site in enumerate(SITES):
            ax = axs[i, j]
            if j == 0:
                ax.text(0.05, 0.9, site.capitalize(), transform=ax.transAxes, fontdict=dict(weight='bold'))
            dates = [v[1] for v in (ScenariosDatesFresno if site == 'fresno' else ScenariosDatesOakville)
                     if v[0] == clim][0]
            date_budburst = dates.date_budbreak
            date_veraison_beg = dates.date_start_sim
            date_veraison_end = dates.date_end_sim - timedelta(hours=1)
            w = weather[(weather['site'] == site) & (weather['clim'] == clim)].loc[date_budburst: date_veraison_end]
            w.sort_values('time', inplace=True)
            w.loc[:, 'Tac'].resample('D', label='right').max().plot(ax=ax, label='max')
            w.loc[:, 'Tac'].resample('D', label='right').min().plot(ax=ax, label='min')
            # ax.arrow(x=date_veraison_beg, y=40, dx=0, dy=-5, head_length=5)
            ax.annotate("Budburst" if i + j == 0 else "",
                        xy=(date_budburst, 0), xycoords=("data", "axes fraction"),
                        xytext=(date_budburst, 0.2), textcoords=("data", "axes fraction"),
                        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3", facecolor='w'), ha='center')
            ax.annotate("Véraison" if i + j == 0 else "",
                        xy=(date_veraison_beg, 0), xycoords=("data", "axes fraction"),
                        xytext=(date_veraison_beg, 0.2), textcoords=("data", "axes fraction"),
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3"), ha='center')

    axs[0, 0].set_xlim(datetime(1990, 2, 1), datetime(1990, 9, 1))
    axs[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    axs[0, 0].set_ylabel(r'Air temperature ($\rm {^\circ C}$)')
    axs[0, 0].yaxis.set_label_coords(-.25, 0, transform=axs[0, 0].transAxes)
    for ax in axs[-1, :]:
        ax.set_xticklabels(axs[-1, 0].get_xticklabels(), rotation=90)
        ax.set(xlabel='')

    fig.tight_layout()
    fig.subplots_adjust(hspace=0.05)
    fig.savefig(path_fig / 'poster_weather_scenarios.png')

    pass


def plot_temperature_data(path_data: Path, path_fig: Path):
    fig, axs = pyplot.subplots(nrows=len(SITES), ncols=len(SCEN_CLIM), sharey='all', sharex='all')

    traits_ordered = ('baseline', 'high_gmax', 'low_gsp50', 'low_gmax', 'high_gsp50', 'elite')
    df = read_csv(path_data, sep=';', decimal='.', parse_dates=['dt'])
    for i, site in enumerate(SITES):
        for j, clim in enumerate(SCEN_CLIM):
            ax = axs[i, j]
            for k, trait in enumerate(traits_ordered):
                pdf = df[(df['site'] == site) & (df['clim'] == clim) & (df['trait'] == trait)]
                for l, orient in enumerate(SCEN_ORIENT):
                    c = {'north_south': 'yellow', 'northeast_southwest': 'orange', 'east_west': 'red'}[orient]
                    ppdf = pdf[pdf['orient'] == orient].set_index('dt')
                    gppdf = ppdf.resample('D').aggregate(max)
                    bp = ax.boxplot(gppdf['t_q90'], positions=[k], patch_artist=True, sym='')
                    for patch, color in zip(bp['boxes'], [c]):
                        patch.set_facecolor(color)
                    for item in ['boxes', 'whiskers', 'fliers', 'medians', 'caps']:
                        pyplot.setp(bp[item], color=c)
    for ax in axs[-1, :]:
        ax.set_xticks(range(6))
        ax.set_xticklabels(traits_ordered)
        ax.tick_params(axis='x', labelrotation=90)
    for ax, s in zip(axs[:, 0], SITES):
        ax.text(0.05, 0.9, s.capitalize(), transform=ax.transAxes)
    for ax, s in zip(axs[0, :], SCEN_CLIM):
        ax.set_title({'historical': 'Historical', 'rcp45': 'RCP 4.5', 'rcp85': 'RCP 8.5'}[s])
    axs[0, 0].set_ylabel('Maximum daily 90th percentile\nleaf temperature (°C)')
    axs[0, 0].yaxis.set_label_coords(-.25, 0, transform=axs[0, 0].transAxes)
    fig.tight_layout()
    fig.savefig(path_fig / 'temperature_summary1.png')
    pass


if __name__ == '__main__':
    path_root = Path(__file__).parent
    path_figs = path_root / 'figs'
    path_figs.mkdir(exist_ok=True)
    weather_all = get_weather_data(path_sims=path_root.parent / 'sims')
    data_all = get_all_time_series(
        path_time_series=path_root / 'outputs/time_series',
        path_output=path_root / 'outputs/time_series/time_series_all.csv')

    plot_weather_conditions(weather=weather_all, path_fig=path_figs)
    # plot_temperature_data(path_data=path_root / 'outputs/summary_temperature.csv', path_fig=path_figs)

    plot_trait_effect(data=data_all, path_fig=path_figs, is_relative=True)
    plot_trait_effect(data=data_all, path_fig=path_figs, is_relative=False)
    plot_trait_effect(data=data_all, path_fig=path_figs, var_name='An', is_relative=True)
    plot_trait_effect(data=data_all, path_fig=path_figs, var_name='An', is_relative=False)
    # plot_trait_effect(data=data_all, path_fig=path_figs, var_name='Tleaf', is_relative=True)
    # plot_trait_effect(data=data_all, path_fig=path_figs, var_name='Tleaf', is_relative=False)
    plot_water_potential(data=data_all, path_fig=path_figs)
    plot_output(data=data_all, var_name='An', path_fig=path_figs)
    plot_output(data=data_all, var_name='E', path_fig=path_figs)
    # plot_temperature(data=data_all, weather=weather_all, path_fig=path_figs, is_dt=True)
    # plot_temperature(data=data_all, weather=weather_all, path_fig=path_figs, is_dt=False)
