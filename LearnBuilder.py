from __future__ import with_statement
import math
import random
from Builder import Builder


class LearnBuilder(Builder):
    def __init__(self, func, testtype, learn_type='hPES', nperd=30,
                 learn_rate=5e-5, supervision_ratio=0.5,
                 oja=False, seed=None):
        if func == 'channel':
            self.func = LearnBuilder.channel
            self.in_d = 3
            self.out_d = 3
            self.runlength = 30.0
        elif func == 'conv':
            self.func = LearnBuilder.convolution
            self.in_d = 6
            self.out_d = 3
            self.runlength = 80.0
        else:
            raise Exception('Function %s not supported' % func)

        if testtype == 'full':
            if func == 'conv':
                self.train = 4.0
                self.test = 5.0
            elif func == 'channel':
                self.train = 0.5
                self.test = 2.0
        elif testtype == 'one':
            self.train = self.runlength
            self.test = 20.0
        else:
            raise Exception('Test type %s not supported' % testtype)

        self.testtype = testtype
        self.learn_type = learn_type
        self.nperd = nperd
        self.supervision_ratio = supervision_ratio
        self.oja = oja
        self.learn_rate = learn_rate

        # If no seed passed in, we'll generate one
        if seed is None:
            seed = random.randint(0, 0x7fffffff)
        self.seed = seed

        Builder.__init__(self)

    @property
    def params(self):
        p = {
            'learn_type': self.learn_type,
            'nperd': self.nperd,
            'seed': self.seed,
        }

        if self.learn_type != 'control':
            p['learn_rate'] = self.learn_rate

        if self.learn_type == 'PES':
            p['oja'] = self.oja

        if self.learn_type == 'hPES':
            p['supervision_ratio'] = self.supervision_ratio

        return p

    def make(self):
        import nef
        import nef.templates.learned_termination as pes
        import nef.templates.hpes_termination as hpes
        import nef.templates.gate as gating

        if self.net is not None:
            return self.net

        random.seed(self.seed)
        net = nef.Network('Learn Network', seed=random.randrange(0x7fffffff))

        net.make('pre', self.nperd * self.in_d, self.in_d)
        net.make('post', self.nperd * self.out_d, self.out_d)

        net.make_fourier_input('input', dimensions=self.in_d,
                               base=0.25, high=40)

        net.connect('input', 'pre')

        if self.learn_type == 'PES':
            pes.make(net, preName='pre', postName='post', errName='error',
                     N_err=self.nperd * self.out_d, rate=self.learn_rate,
                     oja=self.oja)
        elif self.learn_type == 'hPES':
            hpes.make(net, preName='pre', postName='post', errName='error',
                      N_err=self.nperd * self.out_d, rate=self.learn_rate,
                      supervisionRatio=self.supervision_ratio)
        elif self.learn_type == 'control':
            net.connect('pre', 'post', func=self.func, origin_name='pre_00')
            net.make('error', 1, self.out_d, mode='direct')  # Unused

        net.connect('pre', 'error', func=self.func)
        net.connect('post', 'error', weight=-1)

        start = 'test' if self.testtype == 'full' else 'train'
        net.make_input('switch', LearnBuilder.get_learning_times(
                self.train, self.test, start))

        gating.make(net, name='Gate', gated='error', neurons=50, pstc=0.01)

        net.connect('switch', 'Gate')

        # Calculate actual error
        net.make('actual', 1, self.in_d, mode='direct')
        net.connect('input', 'actual')

        net.make('actual error', 1, self.out_d, mode='direct')
        net.connect('actual', 'actual error', func=self.func)
        net.connect('post', 'actual error', weight=-1)

        self.net = net

        return self.net

    def run(self, name, logdir):
        import nef
        if self.net is None:
            self.make()

        fn = Builder.write_param_file(name, self.params, logdir)

        lognode = nef.Log(self.net, "log", dir=logdir,
                          filename='%s.csv' % fn, interval=0.01)
        lognode.add('switch', origin='origin', tau=0.0)
        lognode.add('actual error')

        if self.testtype == 'full':
            length = LearnBuilder.get_full_length(
                self.runlength, self.train, self.test)
        elif self.testtype == 'one':
            length = self.train + self.test

        self.net.network.run(0, length)
        self.net.network.removeStepListener(lognode)

    @staticmethod
    def get_full_length(length, train, test):
        # We want to train `length` seconds
        # Each training phase is `train` seconds
        # Each testing phase is `test` seconds
        num_phases = math.ceil(length / train) + 1
        return num_phases * (train + test) + test

    @staticmethod
    def get_learning_times(train, test, start='test'):
        def learning_times(x):
            first = test if start == 'test' else train
            if x % (train + test) <= first:
                return 0.0 if start == 'test' else 1.0
            else:
                return 1.0 if start == 'test' else 0.0
        return learning_times
    
    @staticmethod
    def channel(x):
        return x

    @staticmethod
    def convolution(x):
        import numeric
        return numeric.circconv([x[0], x[1], x[2]],
                                [x[3], x[4], x[5]])

