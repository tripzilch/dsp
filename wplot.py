'''Collection of useful Matplotlib snippets.'''
import pylab as pl
from pylab import gcf, gca, subplot, title, plot, rc, axis, xticks, yticks, xlim, ylim

def rc_set_dark_colourscheme():
    # make pretty dark colourscheme for pylab
    global colorscheme
    global cmap_funk, cmap_bifunk
    colorscheme = ['#ccff00', '#0082ff', '#ff0037', '#00ff13', '#5e00ff', 
        '#ffa800', '#00fff2', '#ff00c1', '#77ff00', '#002cff']
    rc('axes',facecolor='k', edgecolor='0.8', linewidth=1, 
        labelcolor='#ccff00', color_cycle=colorscheme,titlesize='small',labelsize='small')
    rc('grid',color='0.5')
    rc('text',color='#ccff00')
    rc('figure', facecolor='k',edgecolor='k')
    rc('savefig', facecolor='k',edgecolor='0.8',format='png') # does not have any effect?
    rc('xtick', color='#ccff00')
    rc('ytick', color='#ccff00')
    rc('image', interpolation='nearest')

    cmap_funk = pl.mpl.colors.LinearSegmentedColormap.from_list('funk', [
        (0,(0,0,0)),
        (.5,(.8,1,0)),
        (1.0,(1,1,1))])
    cmap_bifunk = pl.mpl.colors.LinearSegmentedColormap.from_list('funk', [
        (0,(0,.3,.6)),
        (.5,(0,0,0)),
        (.75,(.8,1,0)),
        (1.0,(1,1,1))])
    
def ax_wave(title='wave', auto=False):
    '''init nice axis for plotting waveforms'''
    ax = gca()
    ax.clear()
    ax.set(title=title, xticks=[], yticks=[-1,0,1], ylim=(-1.1,1.1))
    ax.set_autoscaley_on(auto)    
    ax.grid(True)
    #tight_layout()

def addwplot(x, t, subplot_params=[5,1,1], scale_margin=512):
    row, col, index = subplot_params
    if len(gcf().get_axes()) == 0 or index > row * col:
        subplot_params[2] = index = 1
    subplot(row, col, index)
    subplot_params[2] += 1

    plot(arange(len(x)), x)
    mx = abs(x[scale_margin:-scale_margin]).max() if scale_margin else abs(x).max()
    axis([0, len(x), -mx*1.05, mx * 1.05])
    title(t)        

def ax_pianoroll(title='notes'):
    '''Twelve named semitones on the x-axis. TODO: support more than one octave.'''
    cla()
    title(title)
    xticks(frange(0, 1, npts=12, closed=0), 'C. C# D. D# E. F. F# G. G# A. A# B.'.split())
    yticks(arange(24))
    pl.grid(True, axis='x')
    xlim(-.5/12,11.5/12)
    pl.autoscale(True,axis='y')

def bubble(x,y,s,bc='#88aadd',c='#000000',ec='#000000',size=10,box_alpha=0.4,family='monospace',weight='bold'):
    '''Draw a simple (small) text bubble, centered on (x,y). Intended for use as a custom label marker.'''
    pl.text(x, y, s, weight=weight, size=size, family=family, color=c, ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5,rounding_size=0.7', ec=ec, fc=bc, alpha=box_alpha))
    
def ykticks(ax):
    ax.set_yticklabels(['%dk' % (q/1000) for q in ax.get_yticks()])

def xkticks(ax):
    ax.set_xticklabels(['%dk' % (q/1000) for q in ax.get_xticks()])    
    
class Subplots(object):
    """Utility class to handle subplots.

    nrows -- number of rows
    ncols -- number of columns
    clear -- [True|False] whether to clear the figure and axes
    ax_params -- default axes parameters for each subplot

    A Subplot object has numerical indices (which are zero-based!) and 
    is an iterator. It is also callable with the same zero-based index
    and optional per-subplot axes parameters.
    """
    def __init__(self, nrows, ncols, clear=True, figure=None, **ax_params):
        self.nrows = nrows
        self.ncols = ncols
        self.clear = clear
        self._fig = figure if figure is not None else gcf()
        self.ax_params = ax_params
        self.__iter__()

    def __call__(self, n=None, **more_params):
        '''Select subplot n.
        
        n -- zero-based subplot index or current index if None
        more_params -- additional axes parameters
        '''
        if n is not None:
            self._i = n
        self.current_axes = pl.subplot(self.nrows, self.ncols, self._i + 1)
        #self.current_axes.clear()
        self.current_axes.set(**self.ax_params)
        self.current_axes.set(**more_params)
        tight_layout()
        return self.current_axes

    def __getitem__(self, key):        
        return self(key)

    def next(self, **more_params):
        if self._i >= len(self):
            raise StopIteration
        self(**more_params)
        self._i += 1
        return self.current_axes        

    def __iter__(self):
        if self.clear:
            rc_set_dark_colourscheme()
            self._fig.clear()
        self(0)        
        return self

    def __len__(self):
        return self.nrows * self.ncols

    def __repr__(self):
        return 'Subplots(%d, %d)' % (self.nrows, self.ncols)
