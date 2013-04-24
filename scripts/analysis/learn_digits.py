from glob import glob
import os

import numpy as np
from numpy.lib.stride_tricks import as_strided as ast

actualdata = '../../data/60k10klabel.csv'
resultsdir = '../../results/digits/'

TRAINSAMPLES = 60000


def get_data(fn):
    SAFETY = 20  # go back some lines, just in case

    with open(fn, 'r') as fp:
        ll = [s.strip() for s in fp.readline().split(',')]
        time_ix = ll.index('time')
        learn_ix = ll.index('learning')
        post_ix = ll.index('post')
        line_len = len(fp.readline())

        # Grab the last line
        fp.seek(-line_len * 3, os.SEEK_END)
        fp.readline()
        t = float([s.strip() for s in fp.readline().split(',')][time_ix])
        if t > 3400:
            steps_per_input = 50
        elif t > 2700:
            steps_per_input = 40
        else:
            steps_per_input = 30

    trainlines = TRAINSAMPLES * steps_per_input - SAFETY
    time = []
    post = []

    with open(fn, 'r', 8 << 16) as fp:
        # Seek past the majority of the file
        fp.seek(trainlines * line_len)
        l = fp.readline()  # First line read will be garbage

        for l in fp:
            ll = [s.strip() for s in l.split(',')]
            if float(ll[learn_ix]) > 0:
                continue
            time.append(float(ll[time_ix]))
            p = np.fromstring(ll[post_ix], sep=";")
            post.append(p.reshape((1, p.shape[0])))

    time = np.array(time)
    post = np.vstack(post)

    # If we're mostly done a thing, we'll pad it
    if time.shape[0] % steps_per_input > (steps_per_input - 3):
        # How much do we need to pad?
        pad = steps_per_input - (time.shape[0] % steps_per_input)
        dt = time[-1] / time.shape[0]
        time = np.append(time, time[-1] + (np.arange(pad) + 1) * dt)
        post = np.append(post, np.zeros((pad, post.shape[1])), axis=0)

    return time, post


def block_view(orig, block):
    """Provide a 2D block view to 2D array. No error checking made.
    Therefore meaningful (as implemented) only for blocks strictly
    compatible with the shape of A.

    Note the tuple addition happening!
    """
    if orig.shape[1] == block[1]:
        shape = (orig.shape[0] / block[0],) + block
        strides = (block[0] * orig.strides[0],) + orig.strides
    else:
        shape = (orig.shape[0] / block[0], orig.shape[1] / block[1]) + block
        strides = (block[0] * orig.strides[0],
                   block[1] * orig.strides[1]) + orig.strides
    return ast(orig, shape=shape, strides=strides)


def get_accuracy(time, post, actual):
    if time[-1] > 3400:
        steps_per_input = 50
    elif time[-1] > 2700:
        steps_per_input = 40
    else:
        steps_per_input = 30

    # Analyze blocks of data
    digits = 10
    block = (steps_per_input, digits)
    post_b = block_view(post, block)
    # Get the amount of activation for each digit for each block
    post_sum = post_b.sum(axis=1)
    # Find the maximum for each block
    post_pred = post_sum.argmax(axis=1)
    return float(np.count_nonzero(post_pred == actual)) / post_pred.shape[0]


def get_actual(fn):
    # In this, we know (assume?) that all lines
    # are the same length.
    # If our output array is the right size, we'll
    # know that we've parsed the file correctly.
    with open(fn, 'r') as fp:
        line_len = len(fp.readline())

    actual = []

    with open(fn, 'r', 8 << 16) as fp:
        # Seek past the majority of the file
        fp.seek(TRAINSAMPLES * line_len)

        for l in fp:
            actual.append(np.fromstring(l, sep="\t").argmax())

    return np.array(actual, dtype=int)


if __name__ == '__main__':
    actual = get_actual(actualdata)

    for d_f in glob(resultsdir + 'digits-*.csv'):
        accuracy = get_accuracy(*get_data(d_f), actual=actual)
        print "%s: %1.2f%%" % (d_f, accuracy * 100)
