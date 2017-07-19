from tripzilch.dsp import wplot
import pylab as pl
from scipy.io import wavfile
import pygame

tau = 2*pl.pi
PHI=.5+.5*5**.5

"Sampling rate"
sr = 44100.0

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

def _ch(n):
    return {1:'mono',2:'stereo'}[n]

def a2sound(ar, level=12000.0):
    return pygame.sndarray.make_sound((level * ar).astype('int16'))

def play(ar, level=0.25):
    '''Play the array as a wave through pygame, normalized to a level 0..1.'''
    global sr
    pygame.mixer.quit()
    if ar.ndim == 1:
        pygame.mixer.init(frequency=int(sr), size=-16, channels=1)
    elif ar.ndim == 2 and ar.shape[1] == 2:
        pygame.mixer.init(frequency=int(sr), size=-16, channels=2)
    else:
        print("ERR: array must be 1D (mono) or 2D (stereo) with two colums.")
        return

    sound = pygame.sndarray.make_sound(wav_float_to_int16(ar, level * 32767))
    channel = sound.play()
    return channel

def stop():
    pygame.mixer.stop()

def wav_float_to_int16(ar, level=32760):
    '''Convert float array to int16 array, normalized to a level 0..32767.'''
    return normalize(ar, level=level).astype('int16')

def wav_float_to_int32(ar, level=32760 * 32760):
    '''Convert float array to int32 array, normalized to a level 0..32767.'''
    return normalize(ar, level=level).astype('int32')

def read(infile, to_mono=False):
    '''Load a WAV, normalized to 1.0, optionally converted to mono.'''
    global sr
    sr, ar = wavfile.read(infile)
    attn = ''
    if ar.ndim == 2:
        if to_mono:
            ar = pl.sum(ar, axis=1)
            attn += ' ATTN: Converted from stereo.'
        else:
            attn += ' ATTN: Not mono.'
    if sr != 44100.0:
        attn += ' ATTN: Not 44.1kHz.'
    print('Read %s (%.1fkHz %s).%s' % (infile, sr / 1000.0, _ch(ar.ndim), attn))
    return normalize(ar, 1.0)

def write(ar, outfile, level=32760 * 32760):
    '''Write a WAV, normalized.'''
    global sr
    wavfile.write(outfile, sr, wav_float_to_int32(ar, level))
    print('Written %s (%.1fkHz %s).' % (outfile, sr / 1000.0, _ch(ar.ndim)))

def normalize(ar, level=1.0):
    return ar * (float(level) / abs(ar).max())

def sine(f, phi, L):
    '''Returns L samples of a sinewave of frequency f (Hz) and phase phi.'''
    res = pl.arange(phi, phi + L)
    res *= (f * tau / sr)
    res = pl.sin(res)
    return res

def beep(freq_phase_amp, L):
    '''Additive synthesis of sinewaves.

    freq_phase_amp -- a numpy array with a row for each sinewave, and
    frequency, phase and amplitude in each column.
    L -- length in samples.
    '''
    res = pl.zeros(L)
    ii = pl.arange(L)
    tmp = pl.empty(L)
    for f, p, a in freq_phase_amp:
        pl.multiply(ii, f * tau / sr, tmp)
        pl.add(tmp, p, tmp)
        pl.sin(tmp, tmp)
        pl.multiply(tmp, a, tmp)
        pl.add(res, tmp, res)

    return res

def asynth(f0, L, term_f = lambda f,k: f * k, term_a = lambda f,k: 1.0 / k, term_p=lambda f,k: 0.0, max_f=sr / 2):
    '''Additive synthesis of sinewaves.

    f0 -- base frequency.
    L -- length in samples.
    term_f, term_a, term_p -- functions to produce respectively the frequency,
    amplitude and phases of sine terms. They are passed two arguments, the
    base frequency f0 and the number of the harmonic. The defaults produce the
    harmonics of a sawtooth wave.
    max_f -- maximum frequency, defaults to to sr / 2 (Nyquist frequency).
    '''
    res = pl.zeros(L)
    ii = pl.arange(L)
    tmp = pl.empty(L)
    H = 1
    f = term_f(f0, H)
    while f < max_f:
        a = term_a(f0, H)
        p = term_p(f0, H)
        pl.multiply(ii, f * tau / sr, tmp)
        pl.add(tmp, p, tmp)
        pl.sin(tmp, tmp)
        pl.multiply(tmp, a, tmp)
        pl.add(res, tmp, res)
        H += 1
        f = term_f(f0, H)
    return res

def generate_waveforms(
    N_harmonics=[256]*36, cycles=8, verbose=False,
    name='wave-%03dh-G2-(ii).wav'):
    '''Generate a series of basic additive waveforms with a varying number of harmonics.'''
    f0 = 49.0
    w0 = round(cycles * sr / f0)
    w3 = round(min(3, cycles) * sr / f0) # plot only first three cycles
    f0 = cycles * sr / w0

    pl.clf()
    NW = len(N_harmonics)
    sqrtNW = NW ** .5
    nc = int(pl.ceil(sqrtNW))
    nr = int(pl.ceil(NW / nc))
    for ii, N in enumerate(N_harmonics):
        H = 1.0 + pl.arange(N)
        freqs = f0 * H
        phases = ((ii+1.0) * PHI) * (1**H)
        phases %= 1.0
        amps = 1 / (H**0.5)
        waev = beep(pl.c_[freqs, tau * phases, amps], w0)
        pre_level = abs(waev).max()
        waev /= pre_level
        pl.subplot(nr,nc,ii+1)
        fn = name % N
        pl.title('%s, pre_level = %.2f' % (fn, pre_level))
        pl.yticks([-1,0,1]); pl.xticks([]); pl.grid(True)
        pl.plot(waev[:w3])
        pl.axis([0,w3,-1.1,1.1])
        write(waev, fn) # todo: constant level
        if verbose:
            print("%d. %s, N = %d, pre_level = %.2f" % (ii, fn, N, pre_level))
            print("freqs  = [ %s ]" % wplot.fmtar(freqs, num=5, fmt='%.1f'))
            print("phases = [ %s ]" % wplot.fmtar(phases, num=5, fmt='%.3f'))
            print("amps   = [ %s ]" % wplot.fmtar(amps, num=5, fmt='%.3f'))
    pl.tight_layout()
    return waev


def ADSR(A_D_S_R=(100, 500, .7, 100), L=2000):
    'ADSR envelope.'
    A, D, S, R = A_D_S_R
    return pl.interp(pl.arange(L), [0, A, A+D, L-R, L-1], [0, 1, S, S, 0])

def saw_bass(n, L=4400, env=(100, 500, .7, 100), N_harmonics=32):
    '''Generate a sawtooth beep with ADSR envelope.'''
    H = 1.0 + pl.arange(N_harmonics)
    f0 = 440 * 2**((n - 69) / 12.0)
    saw = beep(pl.c_[f0 * H, H*0, 1 / H], L)
    saw *= ADSR(env, L)
    return saw

def play_melody(notes, samples):
    ch = pygame.mixer.find_channel(True)
    EV = pygame.USEREVENT + 1
    ch.set_endevent(EV)
    for n in notes:
        while ch.get_busy() and pygame.event.wait() != EV:
            pass
        ch.queue(samples[n])

def saw_pad(NN, L=80000, fullness=9, sep=0, env=(3000, 10000, .6, 15000)):
    '''Generate a sawtooth "supersaw" synth pad.'''
    I = pl.arange(L, dtype=float)
    SAW = pl.empty(L, dtype=float)
    r = pl.zeros(L + sep * (len(NN)-1))
    ENV = ADSR(env, L)
    for i in range(fullness):
        detune = ((float(i) / fullness) - 0.5) * .04
        for ni,n in enumerate(NN):
            SAW = I * (midi.freq(n + detune) / sr)
            SAW += pl.rand()
            SAW %= 1.0
            SAW -= 0.5
            SAW *= ENV
            r[ni * sep:ni * sep + L] += SAW
    return r


