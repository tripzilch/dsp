'''Euclidian rhythms'''
import itertools as it

def zipl(a, b): 
     return it.izip_longest(a, b, fillvalue=[])

flatten = it.chain.from_iterable

def E(k, n):
    if k == 0 or n == 0 or k > n:
         return []
     p = [[1]] * k + [[0]] * (n - k)
     while len(p) - ri > 1:
         p, k = [a+b for a,b in zipl(p[:k],p[k:])], min(k, len(p) - k)
     return list(flatten(p))

print E(5, 13)

