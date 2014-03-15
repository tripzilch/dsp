'''Collection of useful Matplotlib snippets.'''

def rc_set_dark_colourscheme():
    # make pretty dark colourscheme for pylab
    global colorscheme
    global cmap_funk, cmap_bifunk
    colorscheme = ['#ccff00', '#0082ff', '#ff0037', '#00ff13', '#5e00ff', 
        '#ffa800', '#00fff2', '#ff00c1', '#77ff00', '#002cff']
    rc('axes',facecolor='k', edgecolor='0.8', linewidth=1, 
        labelcolor='#ccff00', color_cycle=colorscheme,titlesize='small',labelsize='small')
    rc('grid',color='0.8')
    rc('text',color='#ccff00')
    rc('figure', facecolor='k',edgecolor='k')
    rc('savefig', facecolor='k',edgecolor='0.8',format='png') # does not have any effect?
    rc('xtick', color='#ccff00')
    rc('ytick', color='#ccff00')
    rc('image', interpolation='nearest')

    cmap_funk = mpl.colors.LinearSegmentedColormap.from_list('funk', [
        (0,(0,0,0)),
        (.5,(.8,1,0)),
        (1.0,(1,1,1))])
    cmap_bifunk = mpl.colors.LinearSegmentedColormap.from_list('funk', [
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

def ax_pianoroll(title='notes'):
    '''Twelve named semitones on the x-axis. TODO: support more than one octave.'''
    cla()
    pyplot.title(title)
    xticks(frange(0, 1, npts=12, closed=0), 'C. C# D. D# E. F. F# G. G# A. A# B.'.split())
    yticks(arange(24))
    grid(True, axis='x')
    xlim(-.5/12,11.5/12)
    autoscale(True,axis='y')

def bubble(x,y,s,bc='#88aadd',c='#000000',ec='#000000',size=10,box_alpha=0.4,family='monospace',weight='bold'):
    '''Draw a simple (small) text bubble, centered on (x,y). Intended for use as a custom label marker.'''
    text(x, y, s, weight=weight, size=size, family=family, color=c, ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5,rounding_size=0.7', ec=ec, fc=bc, alpha=box_alpha))
    
def ykticks(ax):
    ax.set_yticklabels(['%dk' % (q/1000) for q in ax.get_yticks()])

def xkticks(ax):
    ax.set_xticklabels(['%dk' % (q/1000) for q in ax.get_xticks()])    
