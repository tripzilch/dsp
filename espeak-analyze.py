# load things

#%cd ~/git/tripzilch/dsp/
#%run -i matplotlibsnippets.py
#%run -i wavtools.py
#%run -i midi.py
#%run -i wanalyze.py
#rc_set_dark_colourscheme()

def get_spoken(txt=u"always uncheck the checkbox", fwav="/tmp/check.wav",
    pitch=25, speed=175, gap=5, verbose=False):
    get_ipython().system(u'espeak -p %d -s %d -g %d -w "/tmp/22k.wav" "%s"' % (pitch, speed, gap, txt))
    get_ipython().system(u'sox /tmp/22k.wav -r44100 "%s"' % fwav)
    return WAnalyze(fwav)

#render cepstrogram

for i, p in enumerate([10,20,30,40,50,60,70,80,90]):
    print 'rendering sound ..', p
    w = get_spoken('always uncheck the checkbox ',gap=10, pitch=p)
    play(w.w)
    print 'plotting ..'
    figure(1)
    w.plot_cepstrogram(w.w, step=400)

    figure(3)
    subplot(3,3,i)
    cla()
    tip = sum(maximum(w.cepstrogram,0),axis=0)
    wl = find_peak(tip, argmax(tip))
    freq = sr / ww
    clf()
    plot(tip, lw=2)
    axvline(x=ww, linestyle='--', color='#0088FF')
    title('ceps sum, pitch=%d, freq estf=%5.2f Hz'% (p, ff))
    tight_layout()


## calculate peak power (pp), peak wavelength (zz), etc
#LB = w.cepstrogram.shape[0]
#pp = zeros(LB)
#zz = zeros(LB)
#ss = zeros(LB)
#for i in range(LB):    
#    cc = w.cepstrogram[i,:]
#    zz[i] = cc.argmax()
#    ss[i] = sum(cc[cc>0])
#    pp[i] = cc.max() / (23 + sum(cc[cc>0]))
#figure(1);sca(w.axA)
#plot(w.bins_left + 1600, pp * (1500/pp.max()))


## perform some spot checks
#testx=[14171,22451,23700,30194,56859,65200]
#figure(4)
#clf()
#for i,xx in enumerate(testx):
#    subplot(3,2,i+1)
#    plot(maximum(0,w.cepstrogram[bin_at(xx),:]))
#    ylim(-0.01,0.45)
#    title('cepstrum at t=%d' % xx)
#tight_layout()

#figure(1);sca(w.axA);plot(testx,6*[300],'o')
