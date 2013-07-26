from glob import glob
import os
import os.path
import sys
import zipfile
currentdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(currentdir + '/../nengo')

import numpy as np
import matplotlib
matplotlib.use('Agg')
font = {'family': 'serif', 'serif': 'Times New Roman'}
matplotlib.rc('font', **font)
matplotlib.rc('figure', dpi=100)
matplotlib.rc('svg', fonttype='none')
matplotlib.rc('legend', frameon=False)
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from bootstrap import ci
from LearnBuilder import LearnBuilder

figuredir = currentdir + "/../../figures"
resultsdir = currentdir + "/../../results"


def get_params(fn):
    with open(fn, 'r') as pfile:
        param_s = '\n'.join([s.strip() for s in pfile.readlines()])
    return param_s


def process_csv(fn, func, testtype):
    # Get data
    with open("%s.csv" % fn, 'r', 8 << 16) as fp:
        time, error = get_data(fp, func, testtype)

    loss = np.sum(error[-5:]) if testtype == 'full' else error[-1]
    loss_s = "error = %f\n" % loss

    with open('%s.result' % fn, 'w') as lf:
        lf.write("error = %f" % loss)

    # Plot the error over time, and other info
    gs = gridspec.GridSpec(1, 2, width_ratios=[7, 3])

    # Zip up and remove the txt, csv, and result files
    exts = ('txt', 'csv', 'result')
    with zipfile.ZipFile('%s.zip' % fn, 'w') as zipped:
        for ext in exts:
            base = os.path.basename('%s.%s' % (fn, ext))
            zipped.write('%s.%s' % (fn, ext), arcname=base)

    for ext in exts:
        os.remove('%s.%s' % (fn, ext))

    # Return one of the losses, if a correct one was passed in
    return {
        'status': 'ok',
        'loss': loss,
    }


def read_results_from_zip(zfn):
    with zipfile.ZipFile('%s.zip' % zfn) as zf:
        zfn_b = os.path.basename('%s' % zfn)
        for l in zf.open('%s.result' % zfn_b):
            if 'error' in l:
                loss = float(l.split('=')[1].strip())
                break
    return loss


def plot_learn_curves(channel_zips, conv_zips, rules=('hPES', 'PES'),
                      presentation=False):
    group_by = 'learn_type'

    figsize = (8, 6) if presentation else (5, 4)
    if presentation:
        matplotlib.rc('font', size=18)
    plt.figure(figsize=figsize)

    for func, zips in zip(('channel', 'conv'), (channel_zips, conv_zips)):
        filenames = {'PES': [], 'hPES': [], 'control': []}

        # Group files by group_by
        for zfn in zips:
            zfn_b = os.path.basename('%s' % zfn)
            with zipfile.ZipFile('%s.zip' % zfn) as zf:
                for l in zf.open('%s.txt' % zfn_b):
                    if group_by in l:
                        group = l.split('=')[1].strip()
                        filenames[group].append(zfn)

        # Get the control results
        control = []
        for zfn in filenames['control']:
            with zipfile.ZipFile('%s.zip' % zfn) as zf:
                zfn_b = os.path.basename('%s' % zfn)
                with zf.open("%s.csv" % zfn_b) as fp:
                    time, error = get_data(fp, func, 'full')
                control.append(error)
        control = np.vstack(control)

        # Just take the mean for the control
        control = np.mean(control, axis=0)

        # Get the non-control results
        colors = ('b', 'g')
        for rule, color in zip(rules, colors):
            err = []
            for zfn in filenames[rule]:
                zfn_b = os.path.basename('%s' % zfn)
                with zipfile.ZipFile('%s.zip' % zfn) as zf:
                    with zf.open("%s.csv" % zfn_b) as fp:
                        time, error = get_data(fp, func, 'full')
                    err.append(error)
            err = np.vstack(err) / control
            mean = np.mean(err, axis=0)
            conf = ci(err, axis=0)

            if func == 'channel':
                plt.subplot(122)
                plt.title('Learning transmission')
                plt.ylim(-0.4, 9)
                plt.gca().yaxis.tick_right()
            elif func == 'conv':
                plt.subplot(121)
                plt.title('Learning binding')
                plt.ylabel('Error relative to control mean')
                plt.xticks(np.arange(0, 80, 20))
                plt.xlim((0, 80))
                plt.ylim(0.9, 1.6)
                plt.gca().yaxis.set_ticks_position('left')

            plt.gca().spines['top'].set_visible(False)
            plt.gca().xaxis.set_ticks_position('bottom')

            plt.xlabel('Learning time (seconds)')
            plt.axhline(1.0, lw=1, color='0.3')
            plt.fill_between(time, y1=conf[1], y2=conf[0],
                             color=color, alpha=0.3)
            if presentation:
                rule = 'Combined' if rule == 'hPES' else 'Supervised'
            plt.plot(time, mean, color=color, lw=1, label=rule)
            if len(rules) > 1:
                if presentation:
                    plt.legend(prop={'size':16})
                else:
                    plt.legend(prop={'size':12})

    plt.tight_layout()
    plt.subplots_adjust(wspace=0)
    name = 'fig4-learn-curves' if len(rules) == 2 else 'learncurve-pes'
    ext = 'svg' if presentation else 'pdf'
    plt.savefig('%s/%s.%s' % (figuredir, name, ext), transparent=True)
    print "Saved fig4-learn-curves.%s" % ext
    plt.close()


def plot_params(channel_zips, conv_zips, presentation=False):
    group_by = 'learn_type'
    sort_by = 'error'
    rel_err = {}
    for func, zips in zip(('ch', 'conv'), (channel_zips, conv_zips)):
        data = process_zips(zips)
        control = data['control']
        mean_error = np.mean([v[0] for v in control])
        for learn_type in ('PES', 'hPES'):
            rel_err[func + '-' + learn_type] = np.array(
                [v[0] for v in data[learn_type]]) / mean_error

    figsize = (8, 6) if presentation else (5, 3.5)
    if presentation:
        matplotlib.rc('font', size=18)
    fig = plt.figure(figsize=figsize)
    fontsize = 20 if presentation else 14
    plt.suptitle("Error rates for all parameter sets", fontsize=fontsize)

    plt.subplot(121)
    plt.axhline(1.0, color='k')
    lines = plt.boxplot((rel_err['conv-PES'], rel_err['conv-hPES']), sym='')
    for line in lines.values():
        plt.setp(line, color='black')

    if presentation:
        plt.xticks((1, 2), ('Bind sup.', 'Bind combined'))
    else:
        plt.xticks((1, 2), ('Bind PES', 'Bind hPES'))
    plt.ylabel('Error relative to control mean')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().xaxis.set_ticks_position('bottom')
    plt.gca().yaxis.set_ticks_position('left')

    ax = plt.subplot(122)
    plt.axhline(1.0, color='k')
    lines = plt.boxplot((rel_err['ch-PES'], rel_err['ch-hPES']), sym='')
    for line in lines.values():
        plt.setp(line, color='black')
    if presentation:
        plt.xticks((1, 2), ('Transmit sup.', 'Transmit comb.'))
    else:
        plt.xticks((1, 2), ('Transmit PES', 'Transmit hPES'))
    ax.yaxis.tick_right()
    plt.ylim((0.661, 2.7))
    if not presentation:
        fig.autofmt_xdate(rotation=10)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().xaxis.set_ticks_position('bottom')

    plt.tight_layout()
    plt.subplots_adjust(wspace=0, top=0.92)

    ext = 'svg' if presentation else 'pdf'
    plt.savefig('%s/fig5-param-boxplot.%s' % (figuredir, ext), transparent=True)
    print "Saved fig5-param-boxplot.%s" % ext
    plt.close()


def process_zips(zips, group_by='learn_type', sort_by='error'):
    # group_by is something in .txt (params)
    # sort_by is something in .result (results)
    data = {'PES': [], 'hPES': [], 'control': []}
    for zfn in zips:
        zfn_b = os.path.basename('%s' % zfn)
        with zipfile.ZipFile('%s.zip' % zfn) as zf:
            for l in zf.open('%s.txt' % zfn_b):
                if group_by in l:
                    group = l.split('=')[1].strip()
                    break

            for l in zf.open('%s.result' % zfn_b):
                if sort_by in l:
                    sort = float(l.split('=')[1].strip())
                    break

            data[group].append((sort, zfn))

    # Sort the result
    for result in data.values():
        result.sort()
    return data


def read_nengo_csv(fp):
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


def get_data(fp, func, testtype):
    train = LearnBuilder(func, testtype).train
    test = LearnBuilder(func, testtype).test
    headers, data = read_nengo_csv(fp)
    time = data[0]
    switch = data[1]
    act_err = data[2]

    test_st = np.arange(0, time[-1], train + test)
    test_end = np.arange(test, time[-1], train + test)

    # Sanity check -- should be all 0
    # print np.array([np.sum(
    #     switch[np.where(time == start)[0][0]:np.where(time == end)[0][0]])
    #     for start, end in zip(test_st, test_end)])

    error = np.array([np.sum(np.abs(
        act_err[:, np.logical_and(time >= start, time <= end)]))
        for start, end in zip(test_st, test_end)])
    time = np.arange(len(test_st) - 1) * train
    return time, error

def main(presentation=False):
    funcs = ('channel', 'conv')

    zips = {}
    zips['channel'] = [z[:-4] for z in
                       glob(resultsdir + '/functions-test/channel*.zip')]
    zips['conv'] = [z[:-4] for z in
                    glob(resultsdir + '/functions-test/conv*.zip')]

    for func in funcs:
        data = process_zips(zips[func])

        print "\tResults for %s" % func
        for k, v in data.iteritems():
            print "  %s" % k
            for i, val in enumerate(v):
                print "%d. %s" % (i + 1, val)

    if presentation:
        plot_learn_curves(zips['channel'], zips['conv'],
                          rules=('PES',), presentation=presentation)
    plot_learn_curves(zips['channel'], zips['conv'],
                      presentation=presentation)

    zips['channel'] = [z[:-4] for z in
                       glob(resultsdir + '/functions-optimize/channel*.zip')]
    zips['conv'] = [z[:-4] for z in
                    glob(resultsdir + '/functions-optimize/conv*.zip')]

    plot_params(zips['channel'], zips['conv'], presentation)

if __name__ == '__main__':
    main()
