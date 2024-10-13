from pathlib import Path
from pickle import load

from hydroshoot import display
from matplotlib import pyplot as plt
from openalea.plantgl.all import Viewer

from grapevine_stomatal_traits.sims.preprocess_functions import prepare_mtg

if __name__ == '__main__':
    pth_root = Path(__file__).parent
    for training_system, f_mtg in (('vsp', 'mtg19900715150000_oak_hist.pckl'),
                                   ('sprawl', 'mtg19900715150000_sjv_hist.pckl')):
        g = prepare_mtg(
            path_digit=pth_root.parents[1] / f'sources/mockups/{training_system}/virtual_digit.csv',
            training_system=training_system,
            rotation_angle=0)
        scene = display.visu(g, def_elmnt_color_dict=True, view_result=True)
        Viewer.saveSnapshot(str(pth_root / f'{training_system}_mkp_.png'))

        geom = {sh.id: sh.geometry for sh in scene}

        g.properties()['geometry'] = {sh.id: sh.geometry for sh in scene if
                                      sh.id in g.property('label') and not g.node(sh.id).label.startswith('L')}
        scene = display.visu(g, def_elmnt_color_dict=True, view_result=True)

        with open(pth_root / f_mtg, mode='rb') as f:
            g2, _ = load(f)

        g2.properties()['geometry'] = geom
        scene = display.visu(g2, plot_prop='Ei', fmt='%6.0f', min_value=0, max_value=2000, view_result=True,
                             scene=scene)
        fig, ax = plt.subplots()
        ax.hist(list(g2.property('Ei').values()))
        ax.set(xlabel='Absorbed Photosynthetic Photon Flux Density\n' + r'($\mathregular{\mu mol\/m^{-2}\/s^{-1}}$)',
               ylabel='freq (-)',
               title=training_system)
        fig.tight_layout()

        fig.savefig(pth_root / f'{training_system}.png')
        Viewer.saveSnapshot(str(pth_root / f'{training_system}_mkp.png'))
