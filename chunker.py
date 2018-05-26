import itertools as it
from functools import wraps

'''The Chunker module contains routines for analysing signal data in windowed
chunks.
'''

def chunks(x, window=ones(2048), step=50):
    wlen = len(window)
    chunk_pos = range(0, len(x) - wlen, step)
    for i, p in enumerate(chunk_pos):
        chunk = x[p:p + wlen] * window
        yield chunk, i, p

def chunks_len(x, wlen=2048, step=50):
    return len(range(0, len(x) - wlen, step))

def test1():
    print('test1')

def analyse(x, window=hamming(2048), step=50):
    "Yields spectrum, psd, ac, cepstrum, *chunks(x, window, step)"
    for chunk, i, p in chunks(x, window=window, step=step):
        fftlen = len(chunk) // 2 + 1
        spec = rfft(chunk)
        psd = real(spec * conjugate(spec)) # power spectral density
        ac = real(irfft(psd)[:fftlen]) # autocorrelation
        # cepstrum
        log_sd = log(psd) * .5 # = log(psd ** .5) = log(sd)
        lsd_max, lsd_min = log_sd.max(), log_sd.min()
        log_sd = maximum(log_sd, lsd_max - 10) # clamp to upper 10 units
        ceps = real(irfft(log_sd,)[:fftlen])
        yield spec, psd, ac, ceps, chunk, i, p

        # overlapping           [------+------]  ..  ..
        # windows      [------+------]   [------+..  ..        [------+------]
        # waveformwaveformwaveformwaveformwavefor..  ..rmwaveformwaveformwavefor
        # bins            [---+---][---+---][---+..  ..-][---+---][---+---]
        # xt = (self.bins_left[0] + (wsize - step) / 2.0 , self.bins_left[-1] + (wsize + step) / 2.0, wsize / 2 + 1, 0)

# 
#    def cached_property(f):
#        @wraps(f)
#        def wrapper(s, *a, **k):
#            n = f.__name__
#            if n not in s._cache:
#                s._cache[n] = f(s, *a, **k)
#            return s._cache[n]
#        return property(wrapper)


def slope(ar, dB_octave):
    "Applies a dB_octave slope to ar."    
    i = 1 + arange(0, len(ar)) * dB2a(dB_octave)
    i = i.reshape([-1] + [1] * (impsd.ndim - 1)) # append required number of singleton dimensions
    return ar * i

def dB2p(d):
    "Decibel to power ratio.\n\n    dB2p(6.0) ~= 4.0."
    return 10 ** (d * .1)

def dB2a(d):
    """Decibel to amplitude ratio.

    dB2a(6.0) = sqrt(dB2p(6.0)) = dB2p(3.0) ~= 2.0."""
    return dB2p(d * 0.5)

def a2dB(p):
    "Amplitude ratio to decibel.\n\n    a2dB(2.0) ~= 6.0."
    return 10 * pl.log10(p*p)

def dB2vel(d):
    "Decibel to 7-bit MIDI velocity.\n\n    dB2vel(-6.0) = 64."
    return int(10 ** (d * .1 * .5) * 128)

def dB2rns(d):
    """Decibel to 7-bit MIDI velocity hex string (for renoise).

    dB2rnd(-6.0) = '40'."""
    return '%02X' % dB2vel(d)

def find_peak(ar, lo=0, hi=None, wa=3):
    '''find peak in array using window search around index i with radius r,
       then weighted average radius wa'''
    if not hi:
        hi = len(ar)
    i = lo + argmax(ar[lo:hi])
    ra = ar[i-wa:i+wa+1]
    ra = (ra-ra.min())
    return sum(ra*arange(i-wa, i+wa+1))/sum(ra)

def prw(ar, p=0.5):
    return ar * (arange(len(ar))+1) ** p

def sigmoid(x, threshold=0.25, p=36):
    return 1 / (1 + exp((-x + threshold) * p))
def elliot_sigmoid(x): return x / (1 + abs(x))
def d_elliot_sigmoid(x): return 1 / (1 + abs(x)) ** 2

def smoothstep(edge0, edge1, x):
    x = clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)    
    return x * x * x * (x * (x * 6 - 15) + 10)

def kaiser_beta(beta):
    '''Partial application of kaiser window function.'''
    f = lambda M: kaiser(M, beta)
    f.func_name = 'kaiser%d' % beta
    return f

def widewindow(x, w=hanning(256)):
    '''Apply fade-in/out using resp. the first and last halves of a windowing function.
        x -- input signal
        w -- window function
    '''
    M = len(w) // 2
    r = x[:]
    r[:M] *= w[:M]
    r[-M:] *= w[-M:]
    return r

def track_envelope(wav, smoothing_factor=600):
    wav2 = wav ** 2
    env = empty_like(wav2)
    ndimage.filters.maximum_filter1d(wav2, smoothing_factor, output=env)
    env = sqrt(ndimage.filters.gaussian_filter1d(env, smoothing_factor / 2))
    return env

