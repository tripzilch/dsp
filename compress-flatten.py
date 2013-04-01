from functools import partial
from wavtools import *
from scipy import ndimage

# make pretty dark colourscheme for pylab
rc('axes',facecolor='k', edgecolor='0.8', linewidth=1)
rc('grid',color='0.8')
rc('figure', facecolor='k',edgecolor='k')
rc('savefig', facecolor='k',edgecolor='0.8',extension='png') # does not have any effect?
rc('xtick', color='#ccff00')
rc('ytick', color='#ccff00')

def wave_ax():
    cla()
    xticks([])
    yticks([-1,0,1])
    grid(True)
    ylim(-1.1,1.1)
    #tight_layout()


wav = wavread('d:\\mix\\collected voice clips\\reverse-the-polarity-[cut].wav')
L = len(wav)

wav2 = wav ** 2
wav2 /= wav2.max()

smoothing_factor = 450
env = sqrt(ndimage.filters.gaussian_filter1d(wav2, smoothing_factor))
env /= env.max()

def kneemax(x1,x2,p=8):
    return (x1**p + x2**p) ** (1./p)
    
def comp_gain(x, limit, maxfun=partial(kneemax, p=8)):
    return limit / maxfun(x, limit)

x = arange(L)

figure(2)
cla();
xx=frange(0,1,npts=256)
limit = 0.3
plot(xx, comp_gain(xx, limit, maxfun=maximum), c='.6', lw=3)
knee8 = partial(kneemax, p=8)
plot(xx, comp_gain(xx, limit, maxfun=knee8), c='#00ff00', lw=1.5)
axis([0,1,0,1])
xticks([0,limit,1])
yticks([0,limit,1])
grid(True)
    
figure(1)
wave_ax()
a_env = fill_between(x, -env, env, facecolor='#002244', edgecolor='#003366', lw=1.5)
a_wav = plot(x,wav,c='#00ccff',lw=0.5, alpha=0.4)

gain = comp_gain(env, limit, maxfun=knee8)
cenv = env * gain
cwav = wav * gain
a_cenv = fill_between(x, -cenv, cenv, facecolor='#009966', edgecolor='#00bb77', lw=1.5)
a_cwav = plot(x ,cwav, c='#ccff55', lw=0.7)

show()
