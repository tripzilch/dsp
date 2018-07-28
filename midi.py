import itertools as it
import numpy as np

sr = 44100.0

class NOTES(object):
    """A NOTES object represent a note, or a sequence/chord of notes.

    Initialized with no arguments produces a single C in octave 0:

        >>> C = N = NOTES()
        >>> print(C)
        C

    You can make chords or scales:

        >>> print(C.maj)
        C  E  G

    You can use all sorts of notations:

        >>> NOTES("C#3") == N.Cs3 == N.Db3 == N.Df3
        True
        >>> NOTES("C'") == N.C1
        True

    You can do addition, subtraction transposing. Shifts or exponentiation
    transpose by octaves (both are supported for reasons of operator
    precedence):

        >>> C + 7 == N.G == N.C1 - 5
        True
        >>> N.Eb3 == N.Eb >> 3 == N.Ds4 << 1 == N.E**3 - 1
        True

    You can do the same arithmetic on chords or sequences, which functions in
    principle like a numpy.array with the notes in integer notation:

        >>> print(C.min + N.A)
        A  C' E'

    Concatenate chords or sequences using the | operator:

        >>> C.maj | 'Bb' == C._7
        True

    The following chords and scales are currently defined:

    ========
        maj         C E G
        min         C Eb G
        dim         C Eb Gb
        aug         C E G#
        sus4        C F G
        sus2        C D G
        _7          C E G Bb
        ma7         C E G B
        mi7         C Eb G Bb
        mima7       C Eb G B
        dim7        C Eb Gb A
        mi7b5       C Eb Gb Bb
        ma7b5       C E Gb B
        ma7s5       C E G# B
        ma7sus4     C F G B
        ma7sus2b5   C D F# B
        _7b5        C E Gb Bb
        _7s5        C E G# Bb
        _7sus4      C F G Bb
        _7sus2      C D G Bb
        _9          C E G Bb D'
        mi9         C Eb G Bb D'
        _9sus4      C F G Bb D'
        _6          C E G A
        mi6         C Eb G A
        add2        C D E G
        add9        C E G D'


        major_pentatonic    C  D  E  G  A  C'
        minor_pentatonic    C  Eb F  G  Bb C'
        whole_tone          C  D  E  F# G# A# C'
        blues_minor         C  Eb F  F# G  Bb C'
        blues_major         C  D  D# E  G  A  C'
        major               C  D  E  F  G  A  B  C'
        minor               C  D  D# F  G  G# A# C'
        harmonic_minor      C  D  D# F  G  G# B  C'
        melodic_minor       C  D  D# F  G  A  B  C'

        ionian              C  D  E  F  G  A  B  C'
        dorian              C  D  D# F  G  A  A# C'
        phrygian            C  C# D# F  G  G# A# C'
        lydian              C  D  E  F# G  A  B  C'
        mixolydian          C  D  E  F  G  A  A# C'
        aeolian             C  D  D# F  G  G# A# C'
        locrian             C  C# D# F  F# G# A# C'

        major_phrygian      C  Db E  F  G  Ab Bb C'
        phrygian_dominant   C  Db E  F  G  Ab Bb C'


        enigmatic           C  Db E  F# G# A# B  C'
        overtone            C  D  E  F# G  A  Bb C'

        chromatic           C  C# D  D# E  F  F# G  G# A  A# B  C'

        double_harmonic     C  Db E  F  G  Ab B  C'
        byzantine           C  Db E  F  G  Ab B  C'

    ========

    These chords are actually specified by the above docstring. See the code
    after the end of this class definition.

    Here's some more scales that I'm not 100% sure of their correctness, and
    as long as I don't need them I think it's better to not include them:

        persian             C  Db E  F  Gb Ab B  C'
        oriental            C  Db E  F  Gb A  Bb C'
        major_locrian       C  D  E  F  Gb Ab Bb C'
        hindu               C  D  E  F  G  Ab Bb C'
        lydian_minor        C  D  E  F# G  Ab Bb C'
        leading_whole_tone: C  D  E  F# G# A# B  C'

    """

    def __init__(self, notes='C'):
        if isinstance(notes, str):
            notes = tuple(
                'CCDDEFFGGAAB'.index(n[0])
                + ('#' in n) + ('s' in n) + ('♯' in n)
                - ('b' in n) - ('f' in n) - ('♭' in n)
                + 12 * (1 + "123456789".find(n[-1]))
                for n in notes.replace("'","1").strip().split())
        elif not hasattr(notes, '__iter__'): # iterable?
            notes = (notes,)

        # notes property will always be a tuple of ints
        self.notes = tuple(int(n) for n in notes)

    @property
    def s(self): return str(self)
    @property
    def i(self): return self.notes[0]
    @property
    def f(self): return freq(self.i)
    @property
    def pitch_class(self): return self.i % 12
    @property
    def octave(self): return self.i // 12
    @property
    def note(self): return self.i

    @classmethod
    def fromHz(cls, f, sub=100):
        n = 57 + 12 * np.log2(f / 440.0)
        i = int(round(n))
        f = int((n - i) * sub)
        return cls(i), f

    def __add__(self, other):
        'Transpose sequence/chord.'
        return NOTES(np.array(self) + NOTES(other).notes)
    def __sub__(self, other):
        'Transpose sequence/chord.' ## todo: return numerical if other is NOTES else return NOTES        
        return NOTES(np.array(self) - NOTES(other).notes)
    def __lshift__(self, other):
        'Transpose sequence/chord octave.'
        return self - 12 * int(other)
    def __rshift__(self, other):
        'Transpose sequence/chord octave.'
        return self + 12 * int(other)
    def __pow__(self, other):
        'Transpose sequence/chord octave.'
        return self + 12 * int(other)
    def __or__(self, other):
        'Concatenate sequences/chords.'
        return NOTES(self.notes + NOTES(other).notes)
    def __ror__(self, other):
        'Concatenate sequences/chords.'
        return NOTES(NOTES(other).notes + self.notes)
    def __div__(self, other):
        '''Inversion. NOTES("F A C'")/C == NOTES("C' F' A'")'''
        i = [x % 12 for x in self].index(NOTES(other).pitch_class)
        return NOTES(self.notes[i:]) | NOTES(self.notes[:i])>>1

    def __getattr__(self, k):
        if k in NOTES.chords:
            return self + NOTES(NOTES.chords[k])
        else:
            return NOTES(k)

    def __str__(self):
        octave = " '23456789"
        note =  ['Cn', 'C♯n', 'Dn', 'D♯n', 'En', 'Fn', 'F♯n', 'Gn', 'G♯n', 'An', 'A♯n', 'Bn']
        return ' '.join(note[i % 12].replace('n', octave[i // 12]) for i in self.notes).strip()

    def __array__(self): return np.array(self.notes)
    def __getitem__(self, k): return NOTES(self.notes[k])
    def __iter__(self): return iter(self.notes)
    def __eq__(self, other): return self.notes == other.notes
    def __hash__(self): return hash((NOTES, self.notes))
    def __repr__(self): return 'NOTES("%s")' % self
    def __len__(self): return len(self.notes)
    def __index__(self): return self.i
    def __int__(self): return self.__index__()

# initialize chords from docstring!
NOTES.chords = dict(line.strip().split(None,1)
    for line in NOTES.__doc__.split('========')[-2].strip().split('\n') if line.strip())

C = N = NOTES()

def freq(n):
    if isinstance(n, NOTES):
        n = n.i
    return 440 * 2**((n - 57) / 12.0)

def freq_to_note(f):
    return 57 + 12 * np.log2(f / 440.0)

def note(n):
    i = n
    s = i % 12
    return 'C.C♯D.D♯E.F.F♯G.G♯A.A♯B.'[s * 2: s * 2 + 2] + str(i // 12)

def i2note(ii):
    octave = " '23456789"
    notes =  ['Cn', 'C♯n', 'Dn', 'D♯n', 'En', 'Fn', 'F♯n', 'Gn', 'G♯n', 'An', 'A♯n', 'Bn']
    return ' '.join(notes[int(i)%12].replace('n', octave[int(i)//12]) for i in ii)

def note2i(ss):
    return np.array(['CCDDEFFGGAAB'.index(s[0])
        + ('#' in s)
        + ('s' in s)
        + ('♯' in s)
        - ('b' in s)
        - ('f' in s)
        - ('♭' in s)
        + 12 * (s[-1] == "'")
        + 12 * (s[-1].isdigit() and int(s[-1])) for s in ss.split()])

def print_note_table():
    for n in range(128):
        print('--- sr = %d -------------------------------' % sr)
        if note(n)[:2] == 'C-':
            print()
        print('%3d. %9.3f Hz -- %-4s -- SR / %-8.3f' % (n,freq(n),note(n),sr/freq(n)))

def period_sample_error(sr=sr):
    print('--- sr = %d Hz %s' % (sr, 60 * '-'))
    dd=[]
    for n in range(48):
        f = freq(n)
        ww = sr / f
        er = 100 * (np.log(sr / round(ww)) - np.log(f)) / np.log(2.0 ** (1.0/12))
        d = (er,n,freq(n),note(n),ww)
        dd.append(d)
    dd.sort()
    for d in dd:
        print('ERR %6.3f ct -- %3d -- %9.3f Hz -- %-4s -- %8.3f samples' % d)

def min12(a,b):
    '''Minimal modulo 12 absolute difference.'''
    d = abs((a % 12) - (b % 12))
    return min(d, 12 - d)

def chord_finder(notes, size=3, tres=1):
    '''Find plausible chords of certain size by trying all combinations and
    sorting by minimum interval. Use threshold for filtering too-close chords.'''

    cc = (it.combinations(notes,size))
    combb = ((it.combinations(ccc,2), ccc) for ccc in cc)
    diffs = [(sorted((min12(a,b) for a,b in co)),n) for co,n in combb]
    for dd,nn in sorted(diffs, reverse=True):
        if dd[0] > 1:
            print('%10s %10s' % (dd, NOTES(nn)))

def dB2p(d):
    """Decibel to power ratio. dB2p(6.0) ~= 4.0."""
    return 10 ** (d * .1)

def a2dB(p):
    """Amplitude ratio to decibel. a2dB(2.0) ~= 6.0."""
    return 10 * log10(p*p)

def dB2vel(d):
    """Decibel to 7-bit MIDI velocity. dB2vel(-6.0) = 64."""
    return int(10 ** (d * .1 * .5) * 128)

def dB2rns(d):
    """Decibel to 7-bit MIDI velocity hex string (for renoise). dB2rnd(-6.0) = '40'."""
    return '%02X' % dB2vel(d)

class Necklace(tuple):        
    def __new__(cls, a):        
        a = super().__new__(cls, a)
        a = sorted(a.rot(i) for i in range(len(a)))[0]        
        return a
    
    def rot(self, n):
        n %= len(self)
        return self[n:] + self[:n]
        