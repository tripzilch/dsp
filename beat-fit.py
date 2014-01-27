tt = [46988,697790,1350114,5255531,7210092]
nn = [0,2,4,16,22]

def patpat(tt, nn, stop, sr=44100.):
    '''linear fit beats
    
    tt -- time points in samples
    nn -- beat numbers
    stop -- length of track in seconds
    sr -- sampling rate in samples/sec (default 44100)
    
    returns labels as textfile that can be imported in audacity.'''
    pp = poly1d(polyfit(nn,array(tt)/sr,1))
    N = (pp - stop).r
    X = arange(0, N, 0.25)
    labs = '\n'.join(['%.6f\t%.6f\tP%02d.%02d' % (p,p,i/4,16*(i%4)) for i,p in enumerate(pp(X))])
    return labs

