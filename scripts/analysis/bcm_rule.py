import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
font = {'family': 'serif', 'serif': 'Palatino Linotype'}
matplotlib.rc('font', **font)
matplotlib.rc('figure', dpi=100)
matplotlib.rc('svg', fonttype='none')
matplotlib.rc('legend', frameon=False)
import matplotlib.pyplot as plt

currentdir = os.path.dirname(os.path.realpath(__file__))
figuredir = currentdir + "/../../figures"


def main():
    matplotlib.rc('font', size=20, serif='Palatino Linotype')
    matplotlib.rc('mathtext', fontset='stix')
    theta_1 = 3.0
    def bcm_rule_1(x):
        return x * (x - theta_1)

    x1 = np.arange(0.0, 5.1, 0.1)
    y1 = [bcm_rule_1(x) for x in x1]

    plt.figure(figsize=(8, 3))
    plt.plot(x1, y1, linewidth=2, color='k')
    plt.fill_between(x1[:31], y1[:31], color='r')
    plt.fill_between(x1[30:], y1[30:], color='g')
    plt.axhline(ls='--', lw=1, color='k')
    plt.axis((0.0, 4.35, -2.5, 6.0))
    plt.yticks([0])
    plt.xticks(())
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().xaxis.set_ticks_position('none')
    plt.gca().yaxis.set_ticks_position('none')
    plt.gca().annotate(r"$E[a_j]$",
                       xy=(theta_1, 0), xycoords='data',
                       xytext=(theta_1 - 0.5, 1.8), textcoords='data',
                       size=20, va="center", ha="center",
                       arrowprops=dict(arrowstyle="->",
                                       connectionstyle="arc3, rad=-0.2"))
    plt.xlabel(r"$a_j$")
    plt.ylabel(r"$\Delta \omega_{ij}$")
    plt.savefig('%s/bcm_rule.svg' % figuredir, transparent=True)


if __name__ == '__main__':
    main()
