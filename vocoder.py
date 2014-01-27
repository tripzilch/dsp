# these two scripts contain some utility functions, they are currently only used for reading the wav file (which scipy can also do)
# and generating a nice sounding supersaw synth buzz carrier tone
get_ipython().magic('run -i midi.py')
get_ipython().magic('run -i wavtools.py')

'''
A vocoder is a device that uses a filterbank of bandpass filters to split the modulator signal (voice) into frequency bands. For each of these bands, their individual amplitude envelope is tracked. 
An identical filterbank then splits the carrier signal (often a harmonically rich synth buzz sound), and each of those frequency bands is then individually amplitude-modulated with the corresponding amplitude envelope. These signals are then recombined --> ROBOT VOICE

'''

def truncpad(ar, L):
    '''truncates or zero-pads the array ar to length L'''
    la = len(ar)
    if L > la:
        return r_[ar, zeros(L - la, dtype=ar.dtype)]
    return ar[:L]                

def cos_win(n, L=None): 
    '''return a raised cosine Hann window for n points, truncpadded to length L'''
    return truncpad(.5 - .5 * cos(arange(n) * 2 * pi / n), L or n)

# modulator (voice)
mod = wavread('/home/ritz/monsters2.wav')
# carrier (saw synth buzz)
car = r_[saw_pad(C.E3, 53000, ADSR=(500,1,1,500)),
         saw_pad(C.A2, 73000, ADSR=(500,1,1,500))]
# window size, determines number of freq bands
W = 1024
# step size, determines sensitivity of env tracking
step = 512

WW = max(W, 2 * step)
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
for i in range(0, L - WW, step):
    i_ = slice(i * step, i * step + W)
    mod_fft = fft(mod[i:i+WW] * w_in)
    car_fft = fft(car[i:i+WW] * w_out)
    voc = real(ifft(abs(mod_fft) * car_fft))
    out[i:i+WW] += voc * w_out

play(out)

