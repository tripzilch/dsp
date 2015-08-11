from tripzilch.dsp import midi, wav, wplot
import pylab as pl

wplot.rc_set_dark_colourscheme()

r12 = 2 ** (1.0 / 12)
wav.sr = midi.sr = 48000
nyq = midi.sr / 2.0
fmax = min(19000, nyq)

def err(f, N=1):
    w = midi.sr / f
    wi = round(w * N) / N
    fi = midi.sr / wi
    logf = 1200 * pl.log2(f)
    logfi = 1200 * pl.log2(fi)
    return logfi - logf

def phase_err(f, N=1):
    w = midi.sr / f
    wi = round(w * N) / N
    return wi - w

def generate():
    for n in range(24,108):
        note = midi.note(n).replace('#','s').replace('.','_')
        note, octave = note[:2], note[2:]
        f0 = midi.freq(n)
        w0 = midi.sr / f0
        max_rep = int(20000 / w0)
        reps = pl.argmin([abs(phase_err(f0,i)) for i in range(1, max_rep)]) + 1
        N = int(fmax / f0)
        H = 1.0 + pl.arange(N)
        name = 'saw_{octave}_{note}__{freq:_>7.2f}Hz_{harmonics:_>3}H_x{reps:_<4}.wav'.format(
            freq=f0, note=note, octave=octave, harmonics=N, reps=reps)
        print '{:3} -- {}'.format(n, name)
        # rolloff = interp(f0 * H, [0, fmax, nyq]
        waev = wav.beep(pl.c_[f0 * H, 0 * H, 1 / H], round(w0 * reps))
        wav.write(waev, name)
