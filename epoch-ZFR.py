from tripzilch.dsp import wav, wplot, chunker
import pylab as pl
from scipy import signal

wplot.rc_set_dark_colourscheme()

def load_data(
    fn='/home/ritz/mix/audio samples instruments/sampled vocal/love.wav',
    select=(0, 20000)):
    '''Load selection of test wave file. Apply widewindow fade in/out.'''
    x = wav.read(fn, to_mono=True)
    x = (x[select[0]:select[1]]).astype('float128')
    x = chunker.widewindow(x, pl.kaiser(1500, 15))

sample = load_data()
L = len(sample)
N = 190

# -----------
def ZFR_plot(sample):
    subplots = wplot.Subplots(6, 1)

    s = pl.r_[[0], pl.diff(sample)]
    subplots.next(title='differenced input wave').plot(s)

    #s = signal.lfilter([1], [1, -4, 6, -4, 1], s)
    s = signal.lfilter([1], [1, -2, 1], s)
    subplots.next(title='zero frequency resonator 1').plot(s)

    #    s = zf1 = chunker.sub_mean(s, N)
    s = chunker.sub_poly(s)
    subplots.next(title='zfr1 detrend 1').plot(s)

    s = signal.lfilter([1], [1, -2, 1], s)
    subplots.next(title='zero frequency resonator 2').plot(s)

    #    s = zf2 = chunker.sub_mean(s, N)
    s = zf2 = chunker.sub_poly(s)
    subplots.next(title='zero filtered output (detrend 2)').plot(zf2)

    pl.tight_layout()
    pl.show()

def sub_mean(x, N):
    N = int(N)
    L = len(x)
    y = pl.zeros_like(x)
    ii = pl.arange(-N, N + 1)
    k = 1.0 / len(ii) # 1 / (2 * N + 1)
    for n in range(L):
        iii = pl.clip(ii + n, 0, L - 1)
        s = k * sum(x[iii])
        y[n] = x[n] - s
    print n, x[n], iii[0], iii[-1], s
    return y

def sub_poly(x):
    L = len(x)
    c = pl.polyfit(pl.arange(L), x.astype('float64'), 8)
    p = pl.poly1d(c)(pl.arange(L))
    pl.plot(pl.arange(L), p)
    return x - p

# -----------

def pitch_estimate(dw):
    step = 8
    wsize = 2048
    wfun = pl.ones
    wa = 3
    lo, hi = 50, 700
    hist_params = dict(bins=800, lw=0, range=[lo,hi], rwidth=1.0,
        normed=True, log=True)

    subplots = wplot.Subplots(6, 1,
        yticks=[0,.1,.25,.5,1],
        xlim=(120,240),
        autoscalex_on=False)

    for wfun in [pl.hanning, pl.hamming, pl.blackman, pl.bartlett, pl.ones]:
        cc = chunker.Chunker(dw, window=wfun(wsize), step=step)
        acs = [cc.ac for c in cc.chunks()]
        pp = [chunker.find_peak(a, lo, hi, wa=wa) for a in acs]
        mm = pl.median(pp)
        subplots(
            title='window: %s(%d) step=%s range=%s wa=%d' % (wfun.func_name, wsize, step, [lo,hi], wa),
            xticks=[mm]+range(lo,hi+50,50))
        subplots.next()
        freq, bins, patches = pl.hist(pp, **hist_params)

    print 'Ok!'

'''NOTES
--------------------

# notes v2

1st order zero freq resonator:

    signal.lfilter([1], [1, -2, 1], x)

    y[n]  = 1.0 * x[n] + z0[n - 1]
    z0[n] =            + z1[n - 1] - -2.0 * y[n]
    z1[n] =                        -  1.0 * y[n]

mean filter

    k = 1 / (2 * N + 1)
    signal.lfilter([-k] * N + [1-k] + [-k] * N, [1], x) # N+1 samples delay

    y[n]  =  -k * x[n] + z0[n - 1]
    z0[n] =  -k * x[n] + z1[n - 1]
    z1[n] =  -k * x[n] + z1[n - 1]
    ...
    z{N - 1}[n] = (1 - k) * x[n] + z{N}[n - 1]
    z{N}[n] = -k * x[n] + z{N + 1}[n - 1]
    z{N + 1}[n] = -k * x[n] + z{N + 2}[n - 1]
    z{N + 2}[n] = -k * x[n] + z{N + 3}[n - 1]
    ...
    z{N + N - 1} = -k * x[n]

# notes v1

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

