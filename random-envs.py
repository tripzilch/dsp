class Ops(object):
    def mix(x,y,a):
        return (1.0-a)*x + a*y
        
    def mul(x,ya):
        return (x * ya) % 1.0
        
    def flip(x):
        return 1.0 - x
        
    def sina(x,a): 
        mi=smin(a); ma = smax(a)    
        print mi,ma
        return (sin(x*a*pi) - mi) / (ma - mi)
    
    def smin(a): return sin(minimum(maximum(a * pi, pi),1.5*pi))
    def smax(a): return sin(minimum(a * pi, .5 * pi))
    
    def rf(x, N):
        if N == 0:
            return x
        choose:
            mix(rf(x,N-1), rf(x,N-1), rand())
            mix(rf(x,N-1), rand(), rand())
            mul(rf(x,N-1), rand() * 4)
            mul(rf(x,N-1), rf(x,N-1))
            flip(rf(x,N-1))
            sina(rf(x,N-1), .3 + rand() * 4)