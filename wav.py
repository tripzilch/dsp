import pylab as pl
from scipy.io import wavfile
import pygame

tau = 2*pl.pi
sr = 44100.0

# print '''sr = %.0f Hz.''' % sr

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
        print "ERR: array must be 1D (mono) or 2D (stereo) with two colums."
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

    sr_, wav = wavfile.read(infile)

    if to_mono and wav.ndim == 2:
        wav = pl.sum(wav,axis=1)

    sr_ = float(sr)
    if sr_ != sr:
        sr = sr_
        print '''sr = %.0f Hz.''' % sr

    return normalize(wav, 1.0)

def write(ar, outfile, level=32760 * 32760):
    '''Write a WAV, normalized.'''
    global sr
    wavfile.write(outfile, sr, wav_float_to_int32(ar, level))

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

def generate_waveforms(
    N_harmonics=[8,16,32,64],
    path='/home/ritz/mix/audio samples instruments/basic-waveforms/',
    name='square_rnd_phase-%03dh-G2-(i).wav'):
    '''Generate a series of basic additive waveforms with a varying number of harmonics.'''
    f0 = 49.0
    w0 = pl.round(sr / f0)
    f0 = sr / w0
    pl.clf()
    for ii, N in enumerate(N_harmonics):
        H = 1.0 + 2 * pl.arange(N)
        waev = beep(pl.c_[f0 * H, pl.random(N) * tau, 1 / H], 8 * w0)
        pl.subplot(3,4,ii+1)
        pl.plot(waev)
        write(waev, path + (name % N))

def ADSR((A, D, S, R)=(100, 500, .7, 100), L=2000):
    'ADSR envelope.'
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


