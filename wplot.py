'''Collection of useful Matplotlib snippets.'''
import pylab as pl

rc = pl.rc
rcParams = pl.rcParams

def rc_set_dark_colourscheme():
    # make pretty dark colourscheme for pylab
    global colorscheme
    global cmap_funk, cmap_bifunk
    colorscheme = ['#ccff00', '#0082ff', '#ff0037', '#00ff13', '#5e00ff',
        '#ffa800', '#00fff2', '#ff00c1', '#77ff00', '#002cff']
    rc('axes', facecolor='k', edgecolor='0.3', linewidth=1,
        labelcolor='#ccff00', prop_cycle=pl.cycler(color=colorscheme), 
        titlesize='medium', labelsize='small')
    rc('grid', color='0.25')
    rc('text', color='#ccff00')
    rc('figure', facecolor='k', edgecolor='0.3')
    rc('savefig', facecolor='k', edgecolor='0.3', format='png') # does not have any effect?
    rc('xtick', color='0.6')
    rc('ytick', color='0.6')
    rc('image', interpolation='nearest')
#  dash_capstyle: ['butt' | 'round' | 'projecting']
#  dash_joinstyle: ['miter' | 'round' | 'bevel']
    cmap_funk = pl.mpl.colors.LinearSegmentedColormap.from_list('funk', [
        (0.00, (0.0, 0.0, 0.0)),
        (0.50, (0.8, 1.0, 0.0)),
        (1.00, (1.0, 1.0, 1.0))])
    cmap_bifunk = pl.mpl.colors.LinearSegmentedColormap.from_list('bifunk', [
        (0.00, (0.0, 0.3, 0.6)),
        (0.50, (0.0, 0.0, 0.0)),
        (0.75, (0.8, 1.0, 0.0)),
        (1.00, (1.0, 1.0, 1.0))])

def get_fig(rows=1, cols=1, n=1, pad=0.1, **subplot_kw):
    fig = pl.figure(n)
    fig.clear()
    fig.set_tight_layout({'pad': pad})
    axs = fig.subplots(rows, cols, subplot_kw=subplot_kw)    
    return fig, axs    

def set_framecol(ax, c='#000000'):
    for s in ax.spines.values():
        s.set_color(c)

def fmtar(x, num=3, fmt='%.2f'):
    'Format array.'
    fmtn = ', '.join(num*[fmt]+['...']+num*[fmt])
    rn = range(num) + range(-num, 0)
    return fmtn % tuple(x[rn])

def ax_wave(ax, title='wave', auto=False):
    '''init nice axis for plotting waveforms'''
    ax.clear()
    ax.set(title=title, xticks=[], yticks=[-1, 0, 1], ylim=(-1.1, 1.1))
    ax.set_autoscaley_on(auto)
    ax.grid(True)
    #tight_layout()

def ax_pianoroll(ax, title='notes'):
    '''Twelve named semitones on the x-axis, one octave.'''
    ax.clear()
    ax.set_title(title)
    ax.set_xticks(pl.frange(0, 1, npts=12, closed=0), 'C. C# D. D# E. F. F# G. G# A. A# B.'.split())
    ax.set_yticks(pl.arange(24))
    ax.set_grid(True, axis='x')
    ax.set_xlim(-.5/12, 11.5/12)
    ax.set_autoscale(True, axis='y')

def bubble(ax, x, y, s, bc='#88aadd', c='#000000', ec='#000000', size=10, 
        box_alpha=0.4, family='monospace', weight='bold'):
    '''Draw a simple (small) text bubble centered on (x, y). Intended for use as a custom label marker.'''
    ax.text(x, y, s, weight=weight, size=size, family=family, color=c, 
        ha='center', va='center', bbox=dict(ec=ec, fc=bc, alpha=box_alpha, 
            boxstyle='round, pad=0.5, rounding_size=0.7'))

def ykticks(ax):
    ax.set_yticklabels(['%dk' % (q/1000) for q in ax.get_yticks()])

def xkticks(ax):
    ax.set_xticklabels(['%dk' % (q/1000) for q in ax.get_xticks()])

