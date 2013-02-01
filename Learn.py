import os.path
import sys
# I make a symlink `trevor` in the nengo directory, pointing to scriptdir
sys.path.append('trevor')  
from Builder import Builder
from LearnBuilder import LearnBuilder

scriptdir = os.path.expanduser("~/nengo-latest/trevor/")

if False:
    builder = LearnBuilder('channel')
    builder.view(True)
else:
    name = sys.argv[1]
    testtype = sys.argv[2]
    params = Builder.parse_params(sys.argv[3:])
    if testtype == 'full':
	    logdir = scriptdir + "results/functions-test"
	elif testtype == 'one':
		logdir = scriptdir + "results/functions-optimize"
    builder = LearnBuilder(name, testtype, **params)
    builder.run(name, logdir)