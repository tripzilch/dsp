from scipy import ndimage

infile = 'd:\\mix\\collected voice clips\\reverse-the-polarity-[cut].wav'

L = len(wav)

wav2 = wav ** 2
wav2 /= wav2.max()

smoothing_factor = 450
env = sqrt(ndimage.filters.gaussian_filter1d(wav2, smoothing_factor))
env /= env.max()

cla()
x=arange(len(wav))
awm = abs(wav).max()
wav2 = wav ** 2
wav2 *= awm / wav2.max()
fill_between(x,-mwav,mwav,facecolor='#00aa55')
plot(x,-wav,c='#00ffaa',lw=0.5)
plot(x,wav,c='#aaff00',lw=0.5)
#plot(x,wav2,c='w',lw=2)
xlim(0,len(wav));ylim(-1,1)
tight_layout()

