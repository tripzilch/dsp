from pylab import *
import itertools as it
from functools import wraps

'''The Chunker module contains routines for analysing signal data in windowed
chunks.
'''

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

class Chunker(object):
    """Manage windowed chunks of waveform"""
    def __init__(self, x, window=hamming(3200), step=50):
        self.x = x
        self.window = window
        self.wlen = len(window)
        self.step = step
        self.chunk_pos = range(0, len(x) - self.wlen, step)
        self.fftlen = self.wlen // 2 + 1
        self._cache = {}

    def at(x): return find(self.chunk_pos > x)[0]

    def __iter__(self):
        for i in self.chunk_pos:
            self.chunk = self.x[i:i + self.wlen] * self.window
            self._cache = {}
            yield self.chunk

        # overlapping           [------+------]  ..  ..
        # windows      [------+------]   [------+..  ..        [------+------]
        # waveformwaveformwaveformwaveformwavefor..  ..rmwaveformwaveformwavefor
        # bins            [---+---][---+---][---+..  ..-][---+---][---+---]
        # xt = (self.bins_left[0] + (wsize - step) / 2.0 , self.bins_left[-1] + (wsize + step) / 2.0, wsize / 2 + 1, 0)

    def chunk_transform(f):
        @wraps(f)
        def wrapper(s, *a, **k):
            n = f.__name__
            if n not in s._cache:
                s._cache[n] = f(s, *a, **k)
            return s._cache[n]
        return property(wrapper)

    @chunk_transform
    def fft(self):
        return rfft(self.chunk)

    @chunk_transform
    def psd(self):
        return real(self.fft * conjugate(self.fft))

    @chunk_transform
    def ac(self):
        return real(irfft(self.psd)[:self.fftlen])

