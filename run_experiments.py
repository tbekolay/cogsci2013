import sys

from learn_runner import learning_test
from hyperopt import fmin, rand, hp
from hyperopt.mongoexp import MongoTrials

# Set of best parameters, from running optimize_performance.py
bests = {
    'hPES': {
        'channel': {
            'nperd': 25,
            'learn_rate': 0.00351890953839,
            'supervision_ratio': 0.798037091828,
        },
        'conv': {
            'nperd': 25,
            'learn_rate': 0.00237897495282,
            'supervision_ratio': 0.725195232663,
        },
    },
    'PES': {
        'channel': {
            'nperd': 25,
            'learn_rate': 0.00202742333273,
            'oja': False,
        },
        'conv': {
            'nperd': 25,
            'learn_rate': 0.00146471927504,
            'oja': False,
        },
    },
    'control': {
        'channel': {
            'nperd': 25,
        },
        'conv': {
            'nperd': 25,
        },
    }
}

if len(sys.argv) == 2:
    max_evals = int(sys.argv[1])
    print "Doing %d runs of all best parameters" % max_evals
else:
    print ("Usage: python run_experiments.py "
           + "<max_evals>")
    sys.exit()


def run(func, learn_type):
    mongo_s = 'localhost:1234/exp'
    trials = MongoTrials('mongo://%s/jobs' % mongo_s,
                         exp_key='%s_%s' % (func, learn_type))

    print "To run jobs, copy the following into a terminal."
    print "hyperopt-mongo-worker --mongo=%s --poll-interval=0.1" % mongo_s

    params = bests[learn_type][func]

    space = {
        'func': hp.choice('func', (func,)),
        'testtype': hp.choice('testtype', ('full',)),
        'learn_type': hp.choice('learn_type', (learn_type,)),
        'nperd': hp.choice('nperd', (params['nperd'],)),
        'seed': hp.choice('seed', range(50)),
    }

    if learn_type != 'control':
        space['learn_rate'] = hp.choice(
            'learn_rate', (params['learn_rate'],))

    if learn_type == 'hPES':
        space['supervision_ratio'] = hp.choice(
            'supervision_ratio', (params['supervision_ratio'],))

    if learn_type == 'PES':
        space['oja'] = hp.choice('oja', (params['oja'],))

    fmin(
        fn=learning_test,
        space=space,
        algo=rand.suggest,
        max_evals=max_evals,
        trials=trials,
    )

    print "%d evaluations finished." % max_evals

run('channel', 'control')
run('channel', 'PES')
run('channel', 'hPES')
run('conv', 'control')
run('conv', 'PES')
run('conv', 'hPES')