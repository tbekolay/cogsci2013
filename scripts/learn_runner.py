"""This file is designed to be called by `hyperopt`.

It runs a Nengo experiment in a subprocess,
then analyzes it using numpy.

"""

from analysis.learn_testing import process_csv, read_results_from_zip
from nengo.Builder import Builder
from nengo.LearnBuilder import LearnBuilder
import os.path
import subprocess as sp

scriptdir = os.path.expanduser("~/nengo-latest/trevor/")
resultsdir = os.path.expanduser("~/Programming/cogsci2013/results/")

def make_argv(func, testtype, params):
    argv = [func, testtype]
    for key in params.keys():
        argv.append(key)
        v = params[key]
        if isinstance(v, float):
            argv.append('float')
        elif isinstance(v, bool):
            argv.append('bool')
        elif isinstance(v, int):
            argv.append('int')
        elif isinstance(v, str):
            argv.append('str')
        else:
            raise Exception('Type is %s' % type(v))
        argv.append(str(v))
    return argv


def run(func, testtype, **params):
    withdefaults = LearnBuilder(func, testtype, **params)

    outfile = (resultsdir + 'functions/'
               + Builder.name_hash(func, withdefaults.params))

    if os.path.exists("%s.zip" % outfile):
        return outfile

    nengo = scriptdir + 'nengo-cl.sh'
    argv = make_argv(func, testtype, withdefaults.params)
    sp.call([nengo, 'Learn.py'] + argv)

    return outfile


def learning_test(params):
    testtype = params['testtype']
    del params['testtype']
    func = params['func']
    del params['func']
    outfile = run(func, testtype, **params)

    if os.path.exists("%s.zip" % outfile):
        return read_results_from_zip(outfile)

    return process_csv(outfile, func, testtype)
