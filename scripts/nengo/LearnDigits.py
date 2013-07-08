import nef
import nef.templates.learned_termination as pes
import nef.templates.hpes_termination as hpes
import nef.templates.gate as gating
import os.path
from datetime import datetime

scriptdir = os.path.expanduser("~/nengo-latest/trevor/")
datadir = os.path.expanduser("~/Code/cogsci2013/data/")
logdir = os.path.expanduser("~/Code/cogsci2013/results/digits/")

# Globals
steps_per_input = 50
dt = 0.001  # Length of timestep
inputs = []
for line in open(datadir + '60k10kinput.csv', 'r'):
    row = [float(x) for x in line.strip().split('\t')]
    inputs.append(row)

IND = len(inputs[0])  # Dimensions of input data

#Reads labels from file
labels = []
for line in open(datadir + '60k10klabel.csv', 'r'):
    row = [float(x) for x in line.strip().split('\t')]
    labels.append(row)

OUTD = len(labels[0])  # Dimensions of label data

#Reads learning switch position (1 or 0) from file
learnswitch = []
for line in open(datadir + '60k10kswitch.csv', 'r'):
    row = [float(x) for x in line.strip().split(',')]
    learnswitch.append(row)


#Gets the input, label, and learning switch for the current time step
class Input(nef.SimpleNode):
    def origin_input(self, dimensions=IND):
        step = int(round(self.t / dt))  # find time step we are on
        # find stimulus to show
        index = (step / steps_per_input) % len(inputs)
        return inputs[index]

    def origin_label(self, dimensions=OUTD):
        step = int(round(self.t / dt))  # find time step we are on
        # find stimulus to show
        index = (step / steps_per_input) % len(inputs)
        return labels[index]

    def origin_learnswitch(self, dimension=1):
        step = int(round(self.t / dt))  # find time step we are on
        # find stimulus to show
        index = (step / steps_per_input) % len(inputs)
        return learnswitch[index]


def make(learn_type='hPES', nperd=20, learn_rate=5e-5,
         supervision_ratio=0.5, oja=False):
    net = nef.Network('Learn Digits')  # creates a network in Nengo
    input = net.add(Input('input'))  # create the input node
    pre = net.make('pre', IND * nperd, IND, radius=4.5)
    post = net.make('post', OUTD * nperd, OUTD, radius=2.5)

    # Create error population
    # Established learning connection between input and output populations
    if learn_type == 'PES':
        pes.make(net, preName='pre', postName='post',
                 errName='error', N_err=OUTD * nperd, rate=learn_rate, oja=oja)
    elif learn_type == 'hPES':
        hpes.make(net, preName='pre', postName='post',
                  errName='error', N_err=OUTD * nperd, rate=learn_rate,
                  supervisionRatio=supervision_ratio)

    # Connect parts of network
    net.connect(input.getOrigin('label'), 'error')
    net.connect(input.getOrigin('input'), pre)
    net.connect('post', 'error', weight=-1)

    # Create a gate for turning learning on and off
    gating.make(net,name='Gate', gated='error', neurons=40, pstc=0.01)

    # Have the 'learning switch position' file drive the gate
    net.connect(input.getOrigin('learnswitch'), 'Gate')
    return net


def run(net, learn_type):

    log_name = 'digits-' + learn_type + "-" + datetime.now().strftime("%Y%m%d-%H_%M_%S") + ".csv"
    logNode = nef.Log(net, "log", dir=logdir, filename=log_name)
    logNode.add('input', name='learning', origin='learnswitch', tau=0.0)
    logNode.add('post')
    simtime = steps_per_input * len(inputs) * dt  # Simulation length
    print "Simulating for %f seconds" % simtime
    net.network.simulator.run(0, simtime, dt, False)


if False:
    net = make(learn_type='PES')
    net.add_to_nengo()
    #net.view()
else:
    import sys

    print sys.argv

    if len(sys.argv) == 1:
        raise Exception("Usage: nengo-cl LearnDigits.py hPES|PES")

    params = {
        'hPES': {
            'nperd': 25,
            'learn_rate': 0.00237897495282,
            'supervision_ratio': 0.725195232663,
        },
        'PES': {
            'nperd': 25,
            'learn_rate': 0.00146471927504,
            'oja': False,
        },
    }

    learn_type = sys.argv[1]
    run(make(learn_type=learn_type, **params[learn_type]), learn_type)
