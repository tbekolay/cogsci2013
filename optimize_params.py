import sys

from learn_runner import learning_test
from hyperopt import fmin, tpe, hp
from hyperopt.mongoexp import MongoTrials

if len(sys.argv) == 4:
    func = sys.argv[1]
    learn_type = sys.argv[2]
    max_evals = int(sys.argv[3])
    print "Testing %s %s %d" % (func, learn_type, max_evals)
else:
    print ("Usage: python optimize_performance.py "
           + "<func> <learn_type> <max_evals>")
    sys.exit()

mongo_s = 'localhost:1234/%s_%s' % (func, learn_type)
trials = MongoTrials('mongo://%s/jobs' % mongo_s, exp_key='0')

print "To run jobs, copy the following into a terminal."
print "hyperopt-mongo-worker --mongo=%s --poll-interval=0.1" % mongo_s

space = {
    'func': hp.choice('func', (func,)),
    'testtype': hp.choice('testtype', ('one',)),
    'learn_type': hp.choice('learn_type', (learn_type,)),
    'nperd': hp.choice('nperd', (25,)),
    'seed': hp.choice('seed', range(10)),
}

if learn_type != 'control':
    space['learn_rate'] = hp.uniform('learn_rate', 1e-7, 1e-2)

if learn_type == 'PES':
    space['oja'] = hp.choice('oja', (False,))

if learn_type == 'hPES':
    space['supervision_ratio'] = hp.uniform('supervision_ratio', 0.1, 0.9)

best = fmin(
    fn=learning_test,
    space=space,
    algo=tpe.suggest,
    max_evals=max_evals,
    trials=trials,
)

print "%d evaluations finished." % max_evals
