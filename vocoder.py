from midi import *
from wav import *

C = NOTES()

'''
A vocoder is a device that uses a filterbank of bandpass filters to split the modulator signal (voice) into 
frequency bands. For each of these bands, their individual amplitude envelope is tracked. 
An identical filterbank then splits the carrier signal (often a harmonically rich synth buzz sound), and 
each of those frequency bands is then individually amplitude-modulated with the corresponding amplitude 
envelope. These signals are then recombined --> ROBOT VOICE

'''

# idea: make (R)LVQ to learn prototypes of modulator-FFT chunks, and 
# apply those to the carrier for extra robotic.
# or perhaps Knn. (but can Knn do relevance learning of freq ranges?)
# once you have prototypes, look for ways to "enhance" the 
# spectrum contrast (and perhaps also equalize peaks)

def truncpad(ar, L):
    '''truncates or zero-pads the array ar to length L'''
    la = len(ar)
    if L > la:
        return r_[ar, zeros(L - la, dtype=ar.dtype)]
    return ar[:L]                

def cos_win(n, L=None): 
    '''return a raised cosine Hann window for n points, truncpadded to length L'''
    return truncpad(.5 - .5 * cos(arange(n) * 2 * pi / n), L or n)

def sigmoid(x, treshold=0.25, p=36):
    return 1 / (1 + exp((-x + treshold) * p))

# modulator (voice)
mod = wavread('/home/gup/Downloads/back.wav', to_mono=True)
# carrier (saw synth buzz)
#car = r_[saw_pad(C.E3, 53000, fullness=25, ADSR=(500,1,1,500)),
#         saw_pad(C.A2, 73000, ADSR=(500,1,1,500))]
car = saw_pad(C.C3, len(mod), fullness=9, ADSR=(500,1,1,500))
#car = wavread('/tmp/buz.wav')

# window size, determines number of freq bands
W = 1024
# step size, determines sensitivity of env tracking
step = 512
WW = max(W, 2 * step)
WW2 = WW * 2
WWh = WW / 2

# consonant detection params
vowel_range = 3200 * WW / sr
fudge = 0.1
consonant_level = 1.0

w_in = cos_win(W, WW)
w_out = cos_win(2 * step, WW) ** 0.5     # use square root because we apply the output window twice, once before the car_fft and once after.
                                         # - if we only apply it before, there's glitchyness because the ffts don't exactly match up
                                         # - if we only apply it after, there might be spectral leakage in the carrier (untested)

L = len(mod)
L += (-L) % step        # this rounds up L to a multiple of step

mod = truncpad(mod, L)
car = truncpad(car, L)

print "Vocoding the shit out of %.2fs of sound." % (L / sr)
print "window size = %d, giving about %.1f frequency bands." % (W, sr / W)
print "step size = %d = %.1fms" % (step, 1000 * step / sr)
out = zeros(L)
irange = range(0, L - WW, step)
spectro = empty((WW, len(irange)))
coco = empty(len(irange))
for ii,i in enumerate(irange):
    mod_fft = fft(mod[i:i + WW] * w_in)
    mod_sd = abs(mod_fft) / WW2
    car_chunk = array(car[i:i + WW])
    
    consonance = (1 + fudge) * sum(mod_sd[vowel_range:WW - vowel_range]) / (fudge + sum(mod_sd))
    #consonance = 0 if consonance < 0.18 else 
    coco[ii] = consonance
    car_chunk += (rand(WW) - 0.5) * consonance * consonant_level
    
    car_fft = fft(car_chunk * w_out)
    voc = real(ifft(mod_sd * car_fft))
    out[i:i + WW] += voc * w_out
    spectro[:, ii] = mod_sd

#play(out)
spec2 = (spectro[:WWh:, :] + spectro[:WWh - 1:-1, :])
clf()
imshow(spec2 ** .5, aspect='auto', origin='lower')

plot(0,0)
plot(coco * 512)
axis([0, spec2.shape[1], 0, spec2.shape[0]])

show()

