import matplotlib
from matplotlib import rcParams

def SM_style():
    # lines
    matplotlib.rc('figure', facecolor ='black')

    rcParams['lines.linewidth']  = 1.5
    rcParams['lines.linestyle']  = '-'
    rcParams['lines.color']      = 'white'

    # fonts & text
    rcParams['font.family']      = 'serif'
    rcParams['font.weight']      = 'normal'
    rcParams['font.size']        = 10.0
    rcParams['text.color']       = 'white'

    # axes & ticks
    rcParams['axes.edgecolor']   = 'white'
    rcParams['axes.facecolor']   = 'black'
    rcParams['axes.linewidth']   = 1.0
    rcParams['axes.grid']        = False
    rcParams['axes.titlesize']   = 'large'
    rcParams['axes.labelsize']   = 'large'
    rcParams['axes.labelcolor']  = 'white'

    rcParams['xtick.major.size'] = 7
    rcParams['xtick.minor.size'] = 4
    rcParams['xtick.major.pad']  = 6
    rcParams['xtick.minor.pad']  = 6
    rcParams['xtick.labelsize']  = 'large'
    rcParams['xtick.minor.width']= 1.0
    rcParams['xtick.major.width']= 1.0

    rcParams['ytick.major.size'] = 7
    rcParams['ytick.minor.size'] = 4
    rcParams['ytick.major.pad']  = 6
    rcParams['ytick.minor.pad']  = 6
    rcParams['ytick.labelsize']  = 'large'
    rcParams['ytick.minor.width']= 1.0
    rcParams['ytick.major.width']= 1.0

    rcParams['xtick.color']  =    'white'
    rcParams['ytick.color']  =    'white'

    # legends
    rcParams['legend.numpoints']= 1
    rcParams['legend.fontsize'] = 'large'
    rcParams['legend.shadow']   = False
    rcParams['legend.frameon']  = False
