import nef
import nef.templates.bcm_termination as bcm
import os.path
import random
from datetime import datetime

scriptdir = os.path.expanduser("~/nengo-latest/trevor/nengo/")
logdir = os.path.expanduser("~/Programming/cogsci2013/results/bcm/")

def make(dims, nperd=20, learn_rate=4e-3, seed=None, regime='bcm'):
    if seed is None:
        seed = random.randint(0, 0x7fffffff)

    random.seed(seed)

    net = nef.Network('BCM Testing', seed=seed)

    net.make('pre', nperd * dims, dims)

    net.make_fourier_input('input', dimensions=dims)
    net.connect('input', 'pre')

    net.make('post', nperd * dims, dims)
    if regime == 'control':
        net.connect('pre', 'post')
    elif regime == 'random':
        def rand_weights(w):
            for i in range(len(w)):
                for j in range(len(w[0])):
                    w[i][j] = random.uniform(-1e-3,1e-3)
            return w
        net.connect('pre', 'post', weight_func=rand_weights)
    else:
        bcm.make(net, preName='pre', postName='post', rate=learn_rate)

    return net


def run(net, name, seed, length, interval=0.01):
    log_name = '%s-%d' % (name, seed)
    logNode = nef.Log(net, "log",
                      dir=logdir, filename=log_name, interval=interval)
    if name == 'bcm':
        logNode.add_transform('post', termination="pre_00")
    logNode.add('post')
    net.network.simulator.run(0, length, 0.001, False)


if False:
    net = make(dims=3)
    net.add_to_nengo()
    net.view()
else:
    dims = 3
    exp_length = 200.0
    exps = 50
    regimes = ('control', 'random', 'bcm')
    for seed in xrange(exps):
        for regime in regimes:
            if os.path.exists("%s/%s-%d.csv" % (logdir, regime, seed)):
                continue
            run(make(dims, regime=regime, seed=seed, nperd=15),
                regime, seed, exp_length, interval=0.25)
