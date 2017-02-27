from wav import *
from wplot import *
from scipy import ndimage
from os import path

COLORS = rcParams['axes.color_cycle']
putng = 81387.0

def bubble(x,y,s,bc='#88aadd',c='#000000',ec='#000000',size=10,box_alpha=0.4,family='monospace',weight='bold'):
    '''Draw a simple (small) text bubble, centered on (x,y). Intended for use as a custom label marker.'''
    text(x, y, s, weight=weight, size=size, family=family, color=c, ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5,rounding_size=0.7', ec=ec, fc=bc, alpha=box_alpha))

def find_peak(ar, i, r=10, wa=3):
    '''find peak in array using window search around index i with radius r,
       then weighted average radius wa'''
    i = i - r + argmax(ar[i-r:i+r+1])
    ra = ar[i-wa:i+wa+1]
    ra = (ra-ra.min())
    return sum(ra*arange(i-wa,i+wa+1))/sum(ra)

def prw(ar, p=0.5):
    return ar * (arange(len(ar))+1) ** p

def sigmoid(x, treshold=0.25, p=36):
    return 1 / (1 + exp((-x + treshold) * p))

def elliot_sigmoid(x): return x / (1 + abs(x))
def d_elliot_sigmoid(x): return 1 / (1 + abs(x)) ** 2

def bin_at(x): return find(w.bins_left>x)[0]

def track_envelope(wav, smoothing_factor=600):
    wav2 = wav ** 2
    env = empty_like(wav2)
    ndimage.filters.maximum_filter1d(wav2, smoothing_factor, output=env)
    env = sqrt(ndimage.filters.gaussian_filter1d(env, smoothing_factor / 2))
    return env


class WAnalyze(object):
    def __init__(self, fn):
        self.fn = fn
        # strip path and extension for plot name/title
        self.name = path.splitext(path.split(fn)[1])[0]
        self.w = wavread(fn, to_mono=True)
        if self.w.size % 2:
            # for simpler fft hackery, make nr of samples even
            self.w = self.w[:-1]

    @property
    def fft(self):
        if not hasattr(self, '_fft'):
            self._fft = rfft(self.w)
            self.L2 = len(self._fft)
        return self._fft

    @property
    def sd(self):
        if not hasattr(self, '_sd'):
            self._sd = real(self.fft * conjugate(self.fft))
        return self._sd

    @property
    def ac(self):
        if not hasattr(self, '_ac'):
            self._ac = real(irfft(self.sd)[:self.L2])
        return self._ac

    def calc_period(self, smooth_factor=100):
        self.ac_smooth = ndimage.filters.gaussian_filter1d(maximum(0, self.ac), smooth_factor)
        self.ac_smooth_p = prw(self.ac_smooth)
        self.period = argmax(self.ac_smooth_p)
        print "Max Period = %d (smoothing=%d)" % (self.period, smooth_factor)

    def plot_all(self):
        self.axA = subplot2grid((6,1),(0,0),4,1); ax_wave('A', auto=True)
        self.axW = subplot2grid((6,1),(4,0),1,1); ax_wave(self.name)
        self.axB = subplot2grid((6,1),(5,0),1,1); ax_wave('B', auto=True)

        self.axW.plot(self.w, lw=0.1)
        self.env = log(track_envelope(self.w))
        self.axB.plot(self.env, lw=2)

        tight_layout()

    def plot_cepstrogram(self, ws, wsize=3200, step=50.0, window_fn=hamming):
        step = float(step)
        self.plot_all()
        win = window_fn(wsize)
        self.bins_left = arange(0, ws.size - wsize, step)
        self.wsize = wsize
        self.cepstrogram = empty((len(self.bins_left), wsize/2+1))
        for i, j in enumerate(self.bins_left):
            chunk = ws[j:j + wsize] * win
            ff = fft(chunk, wsize * 4)
            sd = abs(ff)
            log_sd = log(sd)
            lsd_max, lsd_min = log_sd.max(), log_sd.min()
            log_sd = maximum(log_sd, lsd_max - 10) # ???
            cepstrum = real(ifft(log_sd)[:wsize // 2 + 1])

            self.cepstrogram[i, :] = prw(cepstrum)
        sca(self.axW)
        ax_wave('slice of ' + self.name)
        plot(ws, lw=0.1)
        xlim(0, ws.size - 1)
        sca(self.axA)
        cla()
        # overlapping           [------+------]  ..  ..
        # windows      [------+------]   [------+..  ..        [------+------]
        # waveformwaveformwaveformwaveformwavefor..  ..rmwaveformwaveformwavefor
        # bins            [---+---][---+---][---+..  ..-][---+---][---+---]
        xt = (self.bins_left[0] + (wsize - step) / 2.0 , self.bins_left[-1] + (wsize + step) / 2.0, wsize / 2 + 1, 0)
        cep = self.cepstrogram
        #cep[:,:50] = 0
        #cep[:,-50:] = 0
        imshow(cep.T, aspect='auto', vmin=-cep.max(), cmap=cmap_bifunk, extent=xt)
        axis([0, ws.size - 1, 0, wsize / 2 + 1])
        title('cepstrogram (window size=%d)' % wsize)
        tight_layout()

    def chunked(self, x, window=hamming(3200), step=50):
        'Yields windowed chunks of x.'
        wlen = len(window)
        for j in range(0, len(x) - wlen, step):
            yield x[j:j + wsize] * window
        # overlapping           [------+------]  ..  ..
        # windows      [------+------]   [------+..  ..        [------+------]
        # waveformwaveformwaveformwaveformwavefor..  ..rmwaveformwaveformwavefor
        # bins            [---+---][---+---][---+..  ..-][---+---][---+---]
        # xt = (self.bins_left[0] + (wsize - step) / 2.0 , self.bins_left[-1] + (wsize + step) / 2.0, wsize / 2 + 1, 0)



    def detect_freqs(self, max_freq=666.0):
        figure(3); clf()
        print
        print '-----+-------------------------------------------------', self.name
        fnote = None
        skip = int(sr/max_freq)
        self.segment_freqs = []
        for i,(l,r) in enumerate(self.segments):
            subplot(2,2,i+1)
            bl,br = bin_at(l), bin_at(r)
            cc = sum(self.cepstrogram[bl:br,:], axis=0)
            cc[0:skip] = 0
            cc = ndimage.filters.gaussian_filter1d(cc, 10)
            cc = prw(cc, p=-0.5)
            plot(cc)
            peak = find_peak(cc, argmax(cc))
            freq = sr / peak
            self.segment_freqs.append(freq)
            prev_fnote = fnote
            fnote = freq_to_note(freq) - 24
            nnote = int(round(fnote))
            cents = (fnote - nnote) * 100
            info = '%03d. | %6.2fHz   %s %#+6.2f cents' % (i, freq, note(nnote), cents)
            title(info)
            print info,
            if i > 0:
                print '  interval = %4.2f' % (fnote - prev_fnote)
            else:
                print
            #sca(self.axW)
            #bubble((l+r)/2, 0, note(nnote), box_alpha=0.8)
        tight_layout()

    def segment(self, lo=-3.53, hi=-1.6):
        mid = (lo + hi) / 2
        on = False
        left = None
        self.segments = []
        for i,v in enumerate(self.env):
            if (not on) and v > hi:
                on = True
                left = i
            if on and v < lo:
                on = False
                self.segments.append((left, i))
                self.axB.plot([left,i],[mid,mid], lw=2, c=colorscheme[1])
        return self.segments

'''
(pseudocode-ish)
automatic transient detection and slicing

sr = 44100.0
bpm = 145
tpb = 32

dt = 60. / bpm / tpb
window_size = int(sr * dt)
print("sr=%.1f Hz | %d BPM / %d TPB ~ %.3fms | window_size=%d min_freq=%.1f"
    % (sr, bpm, tpb, dt*1000, window_size, sr / window_size))

# sr=44100.0 Hz | 145 BPM / 32 TPB ~ 12.931ms | window_size=570 min_freq=77.4

fftlen = window_size // 2 + 1    # 286

prev_fft = None
onset_powers = []
for fft in fft_chunks:
    # smooth spectrum, more smoothing to higher freqs
    for i in range(1, fftlen):
        a = exp(i * log(0.5) / fftlen) # exp slope from 0.99.. to 0.5
        fft[i] = (1-a) * fft[i-1] + a * fft[i]

    if prev_fft:
        # only count freq that got louder
        onset_powers.append(sum(maximum(0, fft - prev_fft)))

plot this thing

# hypothesis: best place to slice is at the minimum just *before* an onset
# peak, because you want the full peak at the start of the slice.

optional: zero bottom X percentile of onset_powers to pre-discard tiny transients

perform watershedding algo: returns tree structure of successively finer slices

'''

class Chunker(object):
    """Manage windowed chunks of waveform"""
    def __init__(self, x, window=hamming(3200), step=50):
        self.x = x
        self.window = window
        self.wlen = len(window)
        self.step = step
        self.chunk_pos = range(0, len(x) - wlen, step)
        self.fftlen = self.wlen // 2 + 1

    def chunks(self):
        for i in self.chunk_pos:
            self.chunk = x[i:i + wsize] * window
            yield self.chunk

        # overlapping           [------+------]  ..  ..
        # windows      [------+------]   [------+..  ..        [------+------]
        # waveformwaveformwaveformwaveformwavefor..  ..rmwaveformwaveformwavefor
        # bins            [---+---][---+---][---+..  ..-][---+---][---+---]
        # xt = (self.bins_left[0] + (wsize - step) / 2.0 , self.bins_left[-1] + (wsize + step) / 2.0, wsize / 2 + 1, 0)

    def ffts(self):
        for c in self.chunks():
            self.fft = rfft(c)
            yield self.fft

    def sds(self):
        for f in self.ffts()
            self.sd = real(f * conjugate(f))
            yield self.sd

    def acs(self, i):
        for s in self.sds()
            self.ac = real(irfft(s)[:self.fftlen])
            yield self.acs


