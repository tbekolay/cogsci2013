import numpy as np
from numpy.random import randint


def ci(data, statfunction=np.mean, alpha=0.05, n_samples=10000, axis=0):
    if np.iterable(alpha):
        alphas = np.array(alpha)
    else:
        alphas = np.array([alpha / 2, 1 - alpha / 2])

    bootindices = (randint(data.shape[axis], size=data.shape[axis])
                   for _ in xrange(n_samples))
    stat = np.array([
            statfunction(np.take(data, indices, axis=axis), axis=axis)
            for indices in bootindices])
    
    stat.sort(axis=0)
    nvals = np.round((n_samples - 1) * alphas).astype('int')
    return stat[nvals]
