from pylab import *
from scipy.io import wavfile
import pygame

tau = 2*pi
sr = 44100.0

print '''sr = %.0f Hz.''' % sr

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
    
def wavread(infile, to_mono=False):
    '''Load a WAV, normalized to 1.0, optionally converted to mono.'''    
    global sr
    
    sr_, wav = wavfile.read(infile)

    if to_mono and wav.ndim == 2:
        wav = sum(wav,axis=1)

    sr_ = float(sr)
    if sr_ != sr:
        sr = sr_
        print '''sr = %.0f Hz.''' % sr    

    return normalize(wav, 1.0)
    
def wavwrite(ar, outfile, level=32760 * 32760):
    '''Write a WAV, normalized.'''
    global sr
    wavfile.write(outfile, sr, wav_float_to_int32(ar, level))

def normalize(ar, level=1.0):
    return ar * (float(level) / abs(ar).max())
    

def sinewave(f, phi, L):
    '''Returns L samples of a sinewave of frequency f (Hz) and phase phi.'''
    res = arange(phi, phi + L)
    res *= (f * tau / sr)
    res = sin(res)
    return res

def beep(freq_phase_amp, L):
    '''Additive synthesis of sinewaves.

    freq_phase_amp -- a numpy array with a row for each sinewave, and
    frequency, phase and amplitude in each column.
    L -- length in samples.
    '''
    res = zeros(L)
    ii = arange(L)
    tmp = empty(L)
    for f, p, a in freq_phase_amp:
        multiply(ii, f * tau / sr, tmp)
        add(tmp, p, tmp)        
        sin(tmp, tmp)
        multiply(tmp, a, tmp)
        add(res, tmp, res)

    return res
    
def gen_basic_waveforms():
    f0 = 49.0; w0 = round(sr/f0); f0 = sr / w0
    path = 'd:\\mix\\audio samples instruments\\basic-waveforms\\'
    name = 'square_rnd_phase-%03dh-G2-(i).wav'
    clf()
    for ii,N_harmonics in enumerate([8,16,32,64]):
        H = 1.0 + 2 * arange(N_harmonics)
        waev = beep(c_[f0 * H, random(N_harmonics) * tau, 1 / H], 8 * w0)
        subplot(3,4,ii+1);plot(waev)
        wavwrite(waev, path + (name % N_harmonics))
        
def saw_bass(n, L=4400, ADSR=(100,500,.7,100), N_harmonics=32):
    H = 1.0 + arange(N_harmonics)
    f0 = 440 * 2**((n - 69) / 12.0)
    saw = beep(c_[f0 * H, H*0, 1 / H], L)
    A,D,S,R = ADSR
    saw *= interp(arange(L),[0,A,A+D,L-R,L-1],[0,1,S,S,0])
    return saw

def play_melody(notes, samples):
    ch = pygame.mixer.find_channel(True)
    EV = pygame.USEREVENT + 1
    ch.set_endevent(EV)
    for n in notes:
        while ch.get_busy() and pygame.event.wait() != EV:
            pass
        ch.queue(samples[n])

def saw_pad(NN, L=80000, fullness=9, sep=0, ADSR=(3000, 10000, .6, 15000)):
    I = arange(L, dtype=float)
    SAW = empty(L, dtype=float)
    r = zeros(L + sep * (len(NN)-1))
    A,D,S,R = ADSR
    ENV = interp(arange(L),[0,A,A+D,L-R,L-1],[0,1,S,S,0])
    for i in range(fullness):
        detune = ((float(i) / fullness) - 0.5) * .04
        for ni,n in enumerate(NN):            
            SAW = I * (freq(n + detune) / sr)
            SAW += rand()
            SAW %= 1.0
            SAW -= 0.5
            SAW *= ENV
            r[ni * sep:ni * sep + L] += SAW
    return r


