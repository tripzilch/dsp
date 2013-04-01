from pylab import *
from scipy.io import wavfile
import pygame

tau = 2*pi
SR = 44100.0

print '''SR = %.0f Hz.''' % SR

def play(ar, normalize=0.25):
    '''Play the array as a wave through pygame, normalized to a level 0..1.'''
    global SR
    pygame.mixer.quit()
    if ar.ndim == 1:
        pygame.mixer.init(frequency=int(SR), size=-16, channels=1)
    elif ar.ndim == 2 and ar.shape[1] == 2:
        pygame.mixer.init(frequency=int(SR), size=-16, channels=2)
    else:
        print "ERR: array must be 1D (mono) or 2D (stereo) with two colums."
        return

    sound = pygame.sndarray.make_sound(wav_float_to_int16(ar, normalize))
    channel = sound.play()
    return channel
    
def stop():
    pygame.mixer.stop()

def wav_float_to_int16(ar, normalize=1.0):
    '''Convert float array to int16 array, normalized to a level 0..1.'''
    return normalize(ar, level=32767).astype('int16')

def wavread(infile):
    '''Load a WAV, normalized to 1.0.'''
    global SR
    SR_, wav = wavfile.read(infile)
    SR_ = float(SR)
    if SR_ != SR:
        SR = SR_
        print '''SR = %.0f Hz.''' % SR    
    return normalize(wav, 1.0)
    
def wavwrite(ar, outfile):
    '''Write a WAV, normalized to 1.0.'''
    global SR
    wavfile.write(outfile, SR, wav_float_to_int16(ar))

def normalize(ar, level=1.0):
    return ar * (float(level) / abs(ar).max())
    
