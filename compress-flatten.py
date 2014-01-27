from functools import partial
from wavtools import *
from scipy import ndimage

# make pretty dark colourscheme for pylab
rc('axes',facecolor='k', edgecolor='0.8', linewidth=1, labelcolor='#ccff00')
rc('grid',color='0.8')
rc('text',color='#ccff00')
rc('figure', facecolor='k',edgecolor='k')
rc('savefig', facecolor='k',edgecolor='0.8',extension='png') # does not have any effect?
rc('xtick', color='#ccff00')
rc('ytick', color='#ccff00')

def wave_ax(title='wave'):
    '''init nice axis for plotting waveforms'''
    cla()
    pyplot.title(title)
    xticks([])
    yticks([-1,0,1])
    grid(True)
    ylim(-1.1,1.1)
    #tight_layout()



def track_envelope(wav, smoothing_factor=400):
    wav2 = wav ** 2
    # wav2 /= wav2.max()
    smoothing_factor = 500
    env = empty_like(wav2)
    ndimage.filters.maximum_filter1d(wav2, smoothing_factor, output=env)
    env = sqrt(ndimage.filters.gaussian_filter1d(env, smoothing_factor / 2))
    # env /= env.max()
    return env

def knee(x1,x2,p=8):
    '''Knee function, approaches max/min for positive/negative p.'''
    return (x1**p + x2**p) ** (1./p)
    
def sigmoid(x, treshold=0.25, p=36):
    return 1 / (1 + exp((-x + treshold) * p))
    
def comp_gain(x, target=partial(knee, .4, p=-8)):
    return target(x) / x

# read input sound
import os
#wav = wavread('d:\\mix\\collected voice clips\\reverse-the-polarity-[cut].wav', to_mono=True)

#filename = 'd:\\mix\\collected voice clips\\DickBrain[Coupling02x10].wav'
#filename = 'd:\\mix\\renoise samples\\beat-aknifeandafork.wav' 
filename = 'd:\\mix\\collected voice clips\\reverse-the-polarity-[cut].wav'
wav = wavread(filename, to_mono=True)
L = len(wav)

# get with the COMPRESSION

limit = 0.25

target_k = partial(knee, limit, p=-8)       # soft compression fn (with knee)
#target_k = lambda x: knee(x**2, .35**2, p=-8) / (.35**2)
target_m = partial(minimum, limit)          # hard compression fn

env = track_envelope(wav)
gain = comp_gain(env, target_k)

cenv = env * gain
cwav = wav * gain
menv = track_envelope(cwav)

def comp_draw_garphs():
    # DRAW GARPHS

    figure(2)
    xx=frange(0,1,npts=257)[1:]

    subplot2grid((2,4),(0,0))
    cla();
    title('target')
    plot(xx, target_m(xx), c='.5', lw=4, alpha=0.6)
    plot(xx, target_k(xx), c='#ccff00', lw=1.5)
    axis([0,1,0,1])
    xticks([0,limit,1])
    yticks([0,limit,1])
    grid(True)

    subplot2grid((2,4),(1,0))
    cla();
    title('gain')
    plot(xx, comp_gain(xx, target_m), c='.5', lw=4,alpha=0.6)
    plot(xx, comp_gain(xx, target_k), c='#ccff00', lw=1.5)
    axis([0,1,0,1])
    xticks([0,limit,1])
    yticks([0,limit,1])
    grid(True)
        
    subplot2grid((2,4),(0,1),colspan=3,rowspan=3)
    wave_ax(os.path.basename(filename))

    x = arange(L)
    fill_between(x, -env, env, facecolor='#002244', edgecolor='#003366', lw=1.5)
    plot(x, wav, c='#00ccff', lw=0.5, alpha=0.4)

    fill_between(x, -menv, cenv, facecolor='#009966', edgecolor='#00bb77', lw=1.5)
    plot(x ,cwav, c='#ccff55', lw=0.7)

    tight_layout()
    show()
