import cProfile
from time import sleep, time
from timeit import Timer
__author__ = 'vladsaveliev'

from math import modf, sqrt
from joblib import Parallel, delayed

#r = Parallel(n_jobs=2)(delayed(modf)(i/2.) for i in range(10))
#print r
#res, i = zip(*r)
#print res
#
#print
#
#r = Parallel(n_jobs=4)(delayed(sqrt)(i**2) for i in range(10))
#print r
#
#print
#
#r = Parallel(n_jobs=5, verbose=100)(delayed(sleep)(.1) for _ in range(10))
#
#def f():
#    for i in range(1000):
#        print 13*13
#
#global a
#a = lambda: f()
#
#t = Timer("""a()""")
#print t.timeit()



#timeit.timeit('"-".join(str(n) for n in range(100))', number=10000)

from time import time
start = time()

out = Parallel(n_jobs=2, verbose=1)(delayed(sqrt)(13) for i in range(2))

#print len(out)

if len(out) == 2:
    end = time()
    print end - start
