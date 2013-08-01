from glob import glob
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
font = {'family': 'serif', 'serif': 'Times New Roman'}
matplotlib.rc('font', **font)
matplotlib.rc('figure', dpi=100)
matplotlib.rc('svg', fonttype='none')
matplotlib.rc('legend', frameon=False)
import matplotlib.pyplot as plt

from bootstrap import ci

currentdir = os.path.dirname(os.path.realpath(__file__))
figuredir = currentdir + "/../../figures"

def gini_index(vector):
    # ensure sorted (but don't change original vector)
    v = np.sort(np.abs(vector))
    n = v.shape[0]
    k = np.arange(n) + 1
    l1norm = np.sum(v)
    summation = np.sum((v / l1norm) * ((n - k + 0.5) / n))
    return 1 - 2 * summation


def plot_bars(heights, name):
    plt.figure(figsize=(3, 3))
    plt.bar(np.arange(heights.shape[0]) + 0.5, heights, color='k')
    plt.yticks(())
    plt.xticks(())
    plt.ylim(0, 6)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.savefig('%s/%s.svg' % (figuredir, name), transparent=True)




def main():
    var = 0.3
    dense = np.random.normal(1, var, size=(15,))
    dense.sort()
    sparse = dense.copy()
    sparse[:6] = np.maximum(np.random.normal(0.1, var, size=(6,)), 0)
    sparse[-2:] = np.random.normal(5, var, size=(2,))
    sparse.sort()
    plot_bars(dense, 'dense')
    plot_bars(sparse, 'sparse')
    print gini_index(dense)
    print gini_index(sparse)

if __name__ == '__main__':
    main()
