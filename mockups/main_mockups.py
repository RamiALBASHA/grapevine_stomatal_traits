from pathlib import Path
from statistics import median

import openalea.mtg.mtg
from hydroshoot import architecture, display
from matplotlib import pyplot, image, colors
from numpy import zeros, arange, array
from openalea.mtg import traversal
from openalea.plantgl.all import Scene
from openalea.plantgl.all import surface as surf


def build_mtg(path_csv: Path, is_cordon_preferential_orientation: bool = False) -> openalea.mtg.mtg.MTG:
    g = architecture.vine_mtg(file_path=path_csv)
    cordon_vector = architecture.cordon_vector(g=g)[1] if is_cordon_preferential_orientation else None
    for v in traversal.iter_mtg2(g, g.root):
        architecture.vine_phyto_modular(g, v)
        architecture.vine_axeII(g, v, phyllo_angle=180., PT_init=0.5, insert_angle=46.,
                                insert_angle_CI=4.6, pruning_type='avg_field_model',
                                N_init=0.18, N_max=8, N_max_order=4, in_order_max=35,
                                slope_nfii=5.7, phyto_type='P0', a_L=43.718, b_L=-37.663,
                                a_P=1.722, b_P=10.136, c_P=-5.435, Fifty_cent=400.,
                                slope_curv=70., curv_type='convexe')
        architecture.vine_petiole(g, v, pet_ins=90., pet_ins_cv=0., phyllo_angle=180.)
        architecture.vine_leaf(g, v, leaf_inc=-45., leaf_inc_cv=100., lim_max=12.0, lim_min=5., order_lim_max=6,
                               max_order=55, rand_rot_angle=90.,
                               cordon_vector=cordon_vector)
        architecture.vine_mtg_properties(g, v)
        architecture.vine_mtg_geometry(g, v)
        architecture.vine_transform(g, v)
    return g


def calc_total_leaf_area(g: openalea.mtg.mtg.MTG) -> float:
    total_leaf_area = 0
    for vid in g.VtxList(Scale=3):
        n = g.node(vid)
        if n.label.startswith('L'):
            total_leaf_area += surf(n.geometry)
    return total_leaf_area * 1.e-4


def calc_canopy_volume(g: openalea.mtg.mtg.MTG) -> float:
    """This function supposes that the canopy is aligned to the X axis."""
    x_coords, y_coords, z_coords = zip(*list(g.property('TopPosition').values()))

    cordon_nodes = [g.node(vid).components() for vid in g.VtxList(Scale=2) if g.node(vid).label.startswith('arm')]
    height = median([n.properties()['TopPosition'][-1] for n_group in cordon_nodes for n in n_group])
    y_at_top = [y for (y, z) in zip(y_coords, z_coords) if z >= height]
    width_at_top = max(y_at_top) - min(y_at_top)

    z_at_base = 30  # assumed basic height
    y_at_base = [y for (y, z) in zip(y_coords, z_coords) if z <= z_at_base]
    width_at_base = max(y_at_base) - min(y_at_base)

    # length = max(x_coords) - min(x_coords)

    return 0.5 * (width_at_top + width_at_base) * height * 1.e-4


def get_sprawl_leaf_area_density_from_ref():
    """Grid is taken from Gladstone and Dokoozlian (2003) Vitis 42 (3), 123 – 131"""
    return ([0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [1.9, 5.3, 9.2, 3.7, 0.4],
            [6, 10.5, 7.6, 9.7, 6.6],
            [7.4, 3.6, 0, 8.5, 4.8],
            [7.3, 1, 0, 2.2, 7.1],
            [5.6, 0, 0, 0.9, 6.5])


def plot_leaf_area_density(data: array, ax: pyplot.Subplot = None, norm: colors.Normalize = None,
                           path_fig: Path = None) -> (pyplot.Subplot, image.AxesImage):
    if ax is None:
        fig, ax = pyplot.subplots()
    else:
        fig = ax.get_figure()
    im = ax.imshow(data, cmap='Greens', norm=norm)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            lad = data[i, j]
            ax.text(j, i, f'{lad:.2f}' if lad != 0 else '', ha="center", va="center", color="k", fontsize=8)

    if path_fig is not None:
        fig.savefig(path_fig)

    return ax, im


def calc_leaf_area_density(g: openalea.mtg.mtg.MTG) -> (array, list, list):
    """Grid is taken from Gladstone and Dokoozlian (2003) Vitis 42 (3), 123 – 131,
    This function supposes that the canopy is aligned to the X axis."""
    x_coords, *_ = zip(*list(g.property('TopPosition').values()))
    length = (max(x_coords) - min(x_coords)) * 1.e-2

    y_bounds = [(-75, -45), (-45, -15), (-15, 15), (15, 45), (45, 75)]
    z_bounds = list(zip(range(240, 0, -30), range(270, 30, -30)))
    leaves = [g.node(i) for i in architecture.get_leaves(g=g, leaf_lbl_prefix='L')]

    leaf_area_density = zeros((len(z_bounds), len(y_bounds)))
    for i, z_bound in enumerate(z_bounds):
        for j, y_bound in enumerate(y_bounds):
            leaf_area = 0
            for leaf in leaves:
                y_center = 0.5 * (leaf.properties()['TopPosition'][1] + leaf.properties()['BotPosition'][1])
                z_center = 0.5 * (leaf.properties()['TopPosition'][2] + leaf.properties()['BotPosition'][2])
                if (min(y_bound) <= y_center <= max(y_bound)) and (min(z_bound) <= z_center <= max(z_bound)):
                    leaf_area += surf(leaf.properties()['geometry'])
            leaf_area_density[i, j] = leaf_area * 1.e-4 / length / (
                    (max(z_bound) - min(z_bound)) * (max(y_bound) - min(y_bound)) * 1.e-4)
    return leaf_area_density, y_bounds, z_bounds


def plot_mtg_leaf_area_density(g: openalea.mtg.mtg.MTG, path_fig: Path) -> None:
    leaf_area_density, y_bounds, z_bounds = calc_leaf_area_density(g=g)

    ax, im = plot_leaf_area_density(data=leaf_area_density)
    cbar = ax.figure.colorbar(im, ax=ax, orientation="vertical")
    cbar.ax.set_ylabel(' '.join(('Leaf area density', r'$\mathregular{m^2\/m^{-3}}$')), rotation=270, labelpad=20)
    ax.set_xticks(arange(-0.5, len(y_bounds) - 0.5))
    ax.set_xticklabels([min(y_bound) for y_bound in y_bounds])
    ax.set_yticks(arange(-0.5, len(z_bounds) - 0.5))
    ax.set_yticklabels([min(z_bound) for z_bound in z_bounds])
    ax.get_figure().savefig(path_fig)
    pass


def compare_leaf_area_density(g: openalea.mtg.mtg.MTG, path_fig: Path):
    leaf_area_density_mtg, y_bounds, z_bounds = calc_leaf_area_density(g=g)
    leaf_area_density_ref = get_sprawl_leaf_area_density_from_ref()

    norm = colors.Normalize(0, vmax=10)
    fig, (ax_ref, ax_mtg, ax_cbar) = pyplot.subplots(ncols=3, gridspec_kw=dict(width_ratios=[10, 10, 1]))
    ax_ref, im_ref = plot_leaf_area_density(data=array(leaf_area_density_ref), norm=norm, ax=ax_ref)
    ax_mtg, im_mtg = plot_leaf_area_density(data=leaf_area_density_mtg, norm=norm, ax=ax_mtg)
    cbar = ax_cbar.figure.colorbar(im_ref, cax=ax_cbar, orientation="vertical")
    cbar.ax.set_ylabel(' '.join(('Leaf area density', r'$\mathregular{m^2\/m^{-3}}$')), rotation=270, labelpad=20)
    for ax, s in ((ax_ref, 'ref'), (ax_mtg, 'mtg')):
        ax.set_xticks(arange(-0.5, len(y_bounds) - 0.5))
        ax.set_xticklabels([min(y_bound) for y_bound in y_bounds])
        ax.set_yticks(arange(-0.5, len(z_bounds) - 0.5))
        ax.set_yticklabels([min(z_bound) for z_bound in z_bounds])
        ax.set_title(s)
    ax_ref.set_xlabel('Distance from row center (cm)')
    ax_ref.xaxis.set_label_coords(1.15, -0.15, transform=ax_ref.transAxes)
    ax_ref.set_ylabel('Height (cm)')
    ax_mtg.set_yticklabels([''] * len(ax_mtg.get_yticklabels()))

    ax.get_figure().savefig(path_fig)

    fig.savefig(path_fig)

    pass


if __name__ == '__main__':
    path_root = Path(__file__).parent
    grapevine_mtg = build_mtg(
        path_csv=path_root / 'virtual_digit.csv',
        is_cordon_preferential_orientation=True)
    scene = display.visu(grapevine_mtg, def_elmnt_color_dict=True, scene=Scene(), view_result=True)
    compare_leaf_area_density(g=grapevine_mtg, path_fig=path_root / 'leaf_area_density_mtg.png')
    print(f'total leaf area = {calc_total_leaf_area(g=grapevine_mtg):.2f} m²')
    print(f'canopy volume = {calc_canopy_volume(g=grapevine_mtg):.2f} m3/m-1')
