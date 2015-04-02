from pylab import *
import time

MLS_binary_polynomials = {2: [3], 3: [5, 6], 4: [9, 12],
    5: [18, 20, 23, 30, 27, 29], 6: [33, 48, 51, 57, 45, 54],
    7: [65, 96, 68, 72, 71, 120, 83, 114, 78, 92, 85, 106, 101, 105, 126, 95, 123, 119],
    8: [195, 225, 149, 212, 142, 184, 150, 180, 166, 178, 198, 177, 175, 250, 231, 243],
    9: [264, 272, 300, 308, 408, 281, 393, 401, 278, 360, 432, 269, 450, 323,
        330, 338, 394, 337, 315, 476, 365, 438, 500, 303, 497, 399, 455, 483,
        437, 429, 311, 492, 486, 359, 441, 413, 485, 423, 318, 380, 490, 343,
        350, 378, 347, 378, 509, 447],
    10: [516, 576, 646, 706, 525, 864, 657, 786, 664, 562, 777, 801, 652, 610,
        534, 720, 531, 912, 778, 673, 836, 581, 567, 984, 934, 715, 945, 795,
        754, 670, 938, 683, 711, 966, 924, 627, 873, 813, 931, 907, 969, 807,
        739, 910, 619, 940, 858, 693, 828, 633, 765, 894, 1020, 639, 831, 1017,
        958, 763, 879, 1005],
    11: [1280], 12: [3232], 13: [6912], 14: [12424], 15: [24576], 16: [53256],
    17: [73728], 18: [132096], 19: [466944], 20: [589824], 21: [1310720],
    22: [3145728], 23: [4325376], 24: [14745600], 25: [18874368],
    26: [59244544], 27: [119537664], 28: [150994944], 29: [335544320],
    30: [939524160]}

def MLS(n_bits, which=0, rep=1):
    taps = MLS_binary_polynomials[n_bits][which]
    state0 = state = (1 << n_bits) - 1
    while rep:
        yield state
        state = (state >> 1) ^ -(state & 1) & taps
        if state == state0:
            rep -= 1

def MLS_array(n_bits, which=0, rep=1):
    return (-1.0) ** (fromiter(MLS(n_bits, which, rep), int32) & 1)

debug=False

def auto_corr(x, n, N):
    '''Calculates autocorrelation of sequence x.

    x -- the sequence (array-like)
    n -- the shift
    N -- how many samples from the start to correlate (useful to avoid
        boundary artifacts)
    '''
    L = len(x)
    N1 = min(N, L)
    if n >= L:
        return 0
    if debug and n % 1000 == 0:
        print n,
    x_shift = x[n:n + N1]
    return sum(x[0:min(len(x_shift), N1)] * x_shift) / (N - 1)

def cross_corr(x,y, n, N):
    '''Calculates crosscorrelation of sequences x and y.

    x -- the first sequence (array-like), will be shifted wrt y
    y -- the second sequence (array-like)
    n -- the shift, applied to x
    N -- how many samples from the start of y to correlate (useful to avoid
        boundary artifacts)
    '''
    L = len(x)
    N1 = min(N, L)
    if n >= L:
        return 0
    if debug and n % 1000 == 999:
        elapsed = time.time() - start_time
        print (elapsed/n) * (N-n) / 60.0, 'min'
    x_shift = x[n:n + N1]
    return sum(y[0:min(len(x_shift), N1)] * x_shift) / (N - 1)


class Sequence(object):
    counter = 0
    def __init__(self, name=None, n_bits=8, which=0, mode='mls'):
        if name == None:
            Sequence.counter += 1
            name = 'SEQ.%s' % Sequence.counter
        self.name = name
        if mode == 'mls':
            self.seq = MLS_array(n_bits, which)
        elif mode == 'rnd':
            self.seq = (-1.0) ** randint(2, size=2 ** n_bits - 1)
        else:
            raise ValueError('mode must be either "mls" or "rnd"')
        self.N = len(self)

    @property
    def seq2(self):
        'self.seq, twice'
        return tile(self.seq, 2)

    def get_ac(self):
        'Calculates autocorrelation of Sequence'
        return array([auto_corr(self.seq2, i, self.N) for i in range(self.N)])

    def plot_ac(self, **kw):
        opts = dict(label=self.name, lw=2, alpha=0.5)
        opts.update(kw)
        self.ac = self.get_ac()
        plot(self.ac, **opts)
        xlim(-0.1 * self.N, 1.1 * self.N)
        self.norm2 = norm(self.ac[1:]) ** 2
        print 'norm(%s.ac[1:]) ** 2 = %2.10f' % (self.name, self.norm2)
        return self.ac

    def get_H(self, y):
        '''Calculates impulse response of f for a given y = f(self.seq2).

        y -- f(self.seq2)
        '''
        return array([cross_corr(self.seq2, y, i, self.N) for i in range(self.N)])

    def plot_H(self, y, **kw):
        opts = dict(label=self.name, lw=2, alpha=0.5)
        opts.update(kw)
        H = self.get_H(y)
        plot(H, **opts)
        xlim(-0.1 * self.N, 1.1 * self.N)
        return H

    def __len__(self):
        return len(self.seq)

#figure(1)
#clf()
#mls = Sequence(name='MLS', n_bits=10)
#rnd = Sequence(name='RND', n_bits=10, mode='rnd')
#mls.plot_ac()
#rnd.plot_ac()
#title('Sequence autocorrelations')
#legend()
#xlabel('shift')
#ylabel('autocorrelation')

def transform(x):
    x0 = r_[x, zeros(len(x))]
    shx = lambda i: x0[i:i+len(x)]
    y = (x + 0.3 * shx(150))
    for i in arange(200.0):
        y += shx(250+i) * normpdf(i, 100, 23) * sin(i*0.15) * 10
#    y = sin(y*8)
    return y

#figure()
#title('impulse response of transform')
#mls.plot_H(transform(mls.seq2))

from scipy.io import wavfile

def cut_initial_silence(x, treshold=16, margin=25):
    i = argwhere(abs(x) > treshold)[0,0]
    x = x[i - margin:]

def read_wav(path, **cut_params):
    sr,x = wavfile.read(path)
    cut_initial_silence(x, **cut_params)
    return x / 32768.0

kip_org = read_wav('kip-export-org.wav')
kip_rev = read_wav('kip-export-reverb-medium-nospin.wav')

mls = Sequence(name='MLS18', n_bits=18)
debug=True
start_time = time.time()
#H=mls.get_H(kip_org)

# 3000 - 4:13
# 8000 - 5:19
