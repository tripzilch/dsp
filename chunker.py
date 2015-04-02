from tripzilch.dsp import wav, midi, wplot
from pylab import *
from scipy import ndimage, signal
from os import path

COLORS = wplot.rcParams['axes.color_cycle']

def find_peak(ar, lo=0, hi=None, wa=3):
    '''find peak in array using window search around index i with radius r, 
       then weighted average radius wa'''
    if not hi:
        hi = len(ar)
    i = lo + argmax(ar[lo:hi])
    ra = ar[i-wa:i+wa+1]
    ra = (ra-ra.min())
    return sum(ra*arange(i-wa,i+wa+1))/sum(ra)
    
def prw(ar, p=0.5):
    return ar * (arange(len(ar))+1) ** p

def sigmoid(x, treshold=0.25, p=36):
    return 1 / (1 + exp((-x + treshold) * p))  
def elliot_sigmoid(x): return 1 / (1 + abs(x))
def d_elliot_sigmoid(x): return 1 / (1 + abs(x)) ** 2

def kaiser_beta(beta):
    '''Partial application of kaiser window function.'''
    f = lambda M: kaiser(M, beta)
    f.func_name = 'kaiser%d' % beta
    return f
     
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

    def chunks(self):
        for i in self.chunk_pos:
            self.chunk = self.x[i:i + self.wlen] * self.window
            self._cache = {}
            yield self.chunk

        # overlapping           [------+------]  ..  ..
        # windows      [------+------]   [------+..  ..        [------+------]
        # waveformwaveformwaveformwaveformwavefor..  ..rmwaveformwaveformwavefor
        # bins            [---+---][---+---][---+..  ..-][---+---][---+---]
        # xt = (self.bins_left[0] + (wsize - step) / 2.0 , self.bins_left[-1] + (wsize + step) / 2.0, wsize / 2 + 1, 0)
    
    @property
    def fft(self):
        if 'fft' not in self._cache:
        return self._cache['fft']
                                  
    def ffts(self):
        for c in self.chunks():
            self.fft = rfft(c)
            yield self.fft

    def sds(self):
        for f in self.ffts():
            self.sd = real(f * conjugate(f))
            yield self.sd
        
    def ac(self):
        for s in self.sds():
            self.ac = real(irfft(s)[:self.fftlen])
            yield self.ac







'''
def ZFF(s):
    ' ' 'Zero frequency resonator.

        y0[n] = 4 * y0[n-1] - 6 * y0[n-2] + 4 * y0[n-3] - y0[n-4] + x[n]
        k = 1 / 2 * N + 1
        y[n] = y0[n] - k * SUM(y0[m] for m in range(n-N,n+N+1))


    ' ' '
    x = s[1:] - s[:-1]
    N = 256
    k = 1.0 / (2 * N + 1)
    for n in range(len(x)):
        y0[n] = 4 * y0[n-1] - 6 * y0[n-2] + 4 * y0[n-3] - y0[n-4] + x[n]
        sumy0[n] = sumy0[n-1] - y0[n-2*N-1] + y0[n]
        ' ' ' 
            y[n-N] = y0[n-N] - k * sumy0[n]
            y0[n-N] = y[n-N] + k * sumy0[n]
            y0[n-N] = 4 * (y[n-N-1] + k * sumy0[n-1])
                    - 6 * (y[n-N-2] + k * sumy0[n-2])
                    + 4 * (y[n-N-3] + k * sumy0[n-3])
                    - 1 * (y[n-N-4] + k * sumy0[n-4])
                    + 1 * x[n-N]
            y0[n] = y[n] + k * sumy0[n+N]
            sumy0[n] = sumy0[n-1] - y[n-2*N-1] - k * sumy0[n-N-1] + y[n] + k * sumy0[n+N]
        ' ' '
        y[n-N]  = 4 * (y[n-N-1] + k * sumy0[n-1])
                - 6 * (y[n-N-2] + k * sumy0[n-2])
                + 4 * (y[n-N-3] + k * sumy0[n-3])
                - 1 * (y[n-N-4] + k * sumy0[n-4])
                + 1 * x[n-N] - k * sumy0[n]


    y0=signal.lfilter([1], [1, -4, 6, -4, 1], x)

    
    ' ' 'Zero frequency resonator.

        y0[n] = 4 * y0[n-1] - 6 * y0[n-2] + 4 * y0[n-3] - y0[n-4] + x[n]
        k = 1 / 2 * N + 1
        y[n] = y0[n] - k * SUM(y0[m] for m in range(n-N,n+N+1))

        y[n] = y0[n] - k * SUM(
            4 * y0[m-1] - 6 * y0[m-2] + 4 * y0[m-3] - y0[m-4] + x[m]
            for m in range(n-N,n+N+1))

        y[n] = y0[n] - k * (
            4 * SUM(y0[m] for m in n-N-1 .. n+N-1)
          - 6 * SUM(y0[m] for m in n-N-2 .. n+N-2)
          + 4 * SUM(y0[m] for m in n-N-3 .. n+N-3)
          - 1 * SUM(y0[m] for m in n-N-4 .. n+N-4)

          + 1 * SUM(x[m] for m in n-N,n+N+1))

        y[n] = y0[n] - k * (
          - 1 * y0[n-N-4] 
          + 3 * y0[n-N-3] 
          - 3 * y0[n-N-2] 
          + SUM(y0[n-N-1 .. n+N-4]) 
          + 2 * y0[n+N-3] 
          - 2 * y0[n+N-2] 
          + 4 * y0[n-N-1]
          + 1 * SUM(x[n-N .. n+N]))

    '''

def widewindow(x, w):
    M = len(w) // 2
    r = x[:]
    r[:M] *= w[:M]
    r[-M:] *= w[-M:]
    return r

def sub_mean(x, N):
    N = int(N)
    L = len(x)
    y = zeros_like(x)
    ii = arange(-N, N + 1)
    k = 1.0 / len(ii)
    for n in range(L):
        iii = clip(ii + n, 0, L - 1)
        s = k * sum(x[iii])
        y[n] = x[n] - s
    print n, x[n], iii[0], iii[-1], s
    return y

def sub_poly(x):
    L = len(x)
    c = polyfit(arange(L), x.astype('float64'), 8)
    p = poly1d(c)(arange(L))
    plot(arange(L), p)
    return x - p

if __name__ == '__main__':


    fn='/home/ritz/mix/audio samples instruments/sampled vocal/love.wav'
    s=wav.read(fn, to_mono=True).astype('float128')
    s = s[0:20000]
    s = widewindow(s, kaiser(1500, 15))
    L = len(s)
    N = 190
    clf()

    s = dw = r_[[0], diff(s)]
    wplot.addwplot(dw, 'differenced input wave')

    #s = signal.lfilter([1], [1, -4, 6, -4, 1], s)
    s = zfr1 = signal.lfilter([1], [1, -2, 1], s)
    wplot.addwplot(zfr1, 'zero frequency resonator 1')

#    s = zf1 = sub_mean(s, N)
    s = zf1 = sub_poly(s)
    wplot.addwplot(zf1, 'zfr1 detrend 1')
    s = zfr2 = signal.lfilter([1], [1, -2, 1], s)
    wplot.addwplot(zfr2, 'zero frequency resonator 2')
#    s = zf2 = sub_mean(s, N)
    s = zf2 = sub_poly(s)
    wplot.addwplot(zf2, 'zero filtered output (detrend 2)')

    tight_layout()
    show()