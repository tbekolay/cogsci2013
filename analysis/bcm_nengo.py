import matplotlib
matplotlib.use('Agg')
font = {'family': 'serif', 'serif': 'Times New Roman'}
matplotlib.rc('font', **font)
matplotlib.rc('figure', dpi=100)
import numpy as np
import matplotlib.pyplot as plt
from bootstrap import ci
from glob import glob

figuredir = "../../paper/figures/"


def gini_index(vector):
    # ensure sorted (but don't change original vector)
    v = np.sort(np.abs(vector))
    n = v.shape[0]
    k = np.arange(n) + 1
    l1norm = np.sum(v)
    summation = np.sum((v / l1norm) * ((n - k + 0.5) / n))
    return 1 - 2 * summation


def read_nengo_csv(fn):
    with open(fn, 'r', 8 << 16) as fp:
        l = fp.readline()
        headers = [s.strip() for s in l.split(',')]
        data = [[] for _ in xrange(len(headers))]

        for l in fp:
            for i, col in enumerate([s.strip() for s in l.split(',')]):
                data[i].append(np.fromstring(col, sep=";"))

    for i in xrange(len(data)):
        data[i] = np.vstack(data[i]).T
        if data[i].shape[0] == 1:
            data[i] = data[i].squeeze()

    return headers, data


def get_data(fn):
    headers, data = read_nengo_csv(fn)
    time = data[0]
    post = data[-1]

    if len(headers) == 2:
        # Control or random file: time, post
        return time, post, None

    # BCM file: time, transform, output, post
    transform = data[1]
    return time, post, transform


def sparsity_v(vector):
    sparsity = []
    for i in xrange(vector.shape[1]):
        sparsity.append(gini_index(vector[:,i]))
    return np.array(sparsity)


def get_sparsity(bcm_files):
    tr = []
    for bcm_f in bcm_files:
        t, _, transform = get_data(bcm_f)
        tr.append(sparsity_v(transform))
    tr = np.vstack(tr)
    tr_m = np.mean(tr, axis=0)
    tr_lh = ci(tr, axis=0)
    return t, (tr_lh[0], tr_m, tr_lh[1])


def get_mse(control_files, other_files):
    se = []
    for c_f, o_f in zip(control_files, other_files):
        time, control, _ = get_data(c_f)
        time, other, _ = get_data(o_f)
        se.append(np.sum((control - other) ** 2, axis=0))
    se = np.vstack(se)
    mean = np.mean(se, axis=0)
    conf = ci(se, axis=0)
    return time, conf[0], mean, conf[1]


def plot_bcm(control_files, random_files, bcm_files):
    t, transform = get_sparsity(bcm_files)
    t, rand_l, rand_m, rand_h = get_mse(control_files, random_files)
    t, bcm_l, bcm_m, bcm_h = get_mse(control_files, bcm_files)
    bcm_l[1:] = -1 * (bcm_l[1:] / rand_m[1:]) + 1
    bcm_m[1:] = -1 * (bcm_m[1:] / rand_m[1:]) + 1
    bcm_h[1:] = -1 * (bcm_h[1:] / rand_m[1:]) + 1

    plt.figure(figsize=(5, 4))
    
    plt.subplot(211)
    plt.title("Unsupervised learning in control network")
    plt.ylabel('Transmission accuracy')
    plt.xticks(())
    plt.ylim((0, 1))
    plt.fill_between(t, y1=bcm_l, y2=bcm_h, color='0.7')
    plt.plot(t, bcm_m, color='k')

    plt.subplot(212)
    plt.ylabel('Weight sparsity')
    plt.xlabel('Simulation time (seconds)')
    plt.yticks(np.linspace(0.45, 0.6, 4))
    plt.ylim((0.425, 0.65))
    plt.fill_between(t, y1=transform[0], y2=transform[2], color='0.7')
    plt.plot(t, transform[1], color='k')

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.0)
    plt.savefig('%s/fig3-bcm.pdf' % figuredir)
    print "Saved fig3-bcm.pdf"
    plt.close()


if __name__ == '__main__':
    results_dir = "../results/bcm/"
    control_files = sorted(glob(results_dir + "control-*.csv"))
    random_files = sorted(glob(results_dir + "random-*.csv"))
    bcm_files = sorted(glob(results_dir + "bcm-*.csv"))
    plot_bcm(control_files, random_files, bcm_files)
