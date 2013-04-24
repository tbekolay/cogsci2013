import matplotlib
matplotlib.use('Agg')
font = {'family': 'serif', 'serif': 'Times New Roman'}
matplotlib.rc('font', **font)
matplotlib.rc('figure', dpi=100)
import numpy as np
import matplotlib.pyplot as plt
from bootstrap import ci
from scipy.optimize import curve_fit

figuredir = "../../figures/"

class BCMSim(object):
    def __init__(self, theta, tau_pre, tau_post, pulse_delay, pulse_rate,
           start_omega=None, theta_length=None, num_pairings=10, dt=0.0005):
        self.theta = theta
        self.tau_pre = tau_pre
        self.tau_post = tau_post

        self.pulse_rate = pulse_rate
        self.pulse_gap = 1.0 / self.pulse_rate
        
        if (pulse_delay < 0.0):
            pulse_delay += self.pulse_gap
        self.pulse_delay = pulse_delay
        
        self.start_omega = start_omega
        self.theta_length = theta_length
        self.num_pairings = num_pairings
        self.dt = dt

        self.t = None
        self.a_pre = None
        self.a_post = None
        self.omega = None
    
    @staticmethod
    def filter_spikes(spikes, tau, dt):
        a = np.zeros(len(spikes))
        for i in range(len(a)):
            if i > 0:
                a[i] = a[i-1] - ((a[i-1] / tau) * dt)
            if spikes[i] == 1:
                a[i] += 1.0 / tau  # dt / tau?
        return a

    @staticmethod
    def bcm_filter(a_j, theta):
        return a_j * (a_j - theta) / theta

    @staticmethod
    def _stdp_rule_pre(xdata, amp, tau):
        return amp * np.exp(-xdata / tau)

    @staticmethod
    def _stdp_rule_post(xdata, amp, tau):
        return amp * np.exp(xdata / tau)

    @staticmethod
    def fit_stdp_curve(x, y):
        pre = x > 0
        popt_pre, _ = curve_fit(BCMSim._stdp_rule_pre,
                                x[pre], y[pre], p0=[0.8, 0.01])
        # print popt_pre
        # print np.sum((y[pre] - BCMSim._stdp_rule_pre(
        #     x[pre], *popt_pre)) ** 2, axis=0)

        post = x < 0
        popt_post, _ = curve_fit(BCMSim._stdp_rule_post,
                                 x[post], y[post], p0=[-0.8, 0.01])
        # print popt_post
        # print np.sum((y[post] - BCMSim._stdp_rule_post(
        #     x[post], *popt_post)) ** 2, axis=0)

        x = np.linspace(-0.1, 0.1, 201)
        y = np.zeros_like(x)
        y[x > 0] = BCMSim._stdp_rule_pre(x[x > 0], *popt_pre)
        y[x < 0] = BCMSim._stdp_rule_post(x[x < 0], *popt_post)
        y[x == 0] = np.nan
        
        return x, y

    def run(self):
        # Set up time axis
          # in s
        t_len = self.pulse_gap * (self.num_pairings)
        self.t = np.arange(0.0, t_len + self.dt, self.dt)
  
        # Set up post spike train
        s_post = np.zeros_like(self.t)
        s_post[range(0, int(t_len / self.dt),
                     int(self.pulse_gap / self.dt))] = 1
        self.a_post = BCMSim.filter_spikes(s_post, self.tau_post, self.dt)
  
        # Set up pre spike train
        s_pre = np.zeros_like(self.t)
        s_pre[range(int(self.pulse_delay / self.dt), int(t_len / self.dt),
                    int(self.pulse_gap / self.dt))] = 1
        self.a_pre = BCMSim.filter_spikes(s_pre, self.tau_pre, self.dt)
  
        # Use BCM filter to find change in omega over time
        self.omega = np.zeros_like(self.t)

        if self.start_omega is not None:
            self.omega[0] = self.start_omega

        for i in range(1, self.omega.shape[0]):
            if self.theta_length is not None:
                 self.theta -= self.theta / self.theta_length
                 self.theta += ((self.a_post[i-1] - self.theta)
                                / self.theta_length)
            self.omega[i] = self.omega[i-1] + (
                self.a_pre[i-1] * BCMSim.bcm_filter(
                    self.a_post[i-1], self.theta) * self.dt)

        return self.t, self.a_pre, self.a_post, self.omega, self.theta

    def plot_activity(self, name):
        if self.t is None:
            self.run()
      
        plt.figure(figsize=(6,8))

        # plt.title("Pulse delay: " + str(round(pulse_delays[ix],2)))
        plt.plot(self.t, self.a_pre, lw=1.5, label='Presynaptic')
        plt.plot(self.t, self.a_post, lw=1.5, label='Postsynaptic')
        plt.plot(self.t, self.omega, lw=1.5, label='Weight')
        plt.legend(loc=2)
        plt.axhline(lw=1.0, color='k')
        plt.axis([0.0, self.t[-1],
                  min(np.amin(self.omega), -10),
                  max(np.amax(self.omega),130)])
        plt.savefig('%s/%s.pdf' % (figuredir, name))
        print "Saved %s.pdf" % name
        plt.close()


def plot_stdp_curves(sim, exp):
    plt.figure(figsize=(4.5, 3.5))
    plt.title('Replicated STDP curve')
    
    plt.scatter(sim['x'], sim['y'], color='0.6', label="Simulation")
    plt.scatter(exp['x'], exp['y'], color='0.6', facecolor='w',
                label="Experiment")
    plt.plot(sim['fit_x'], sim['fit_y'], ls='--', lw=1.5, color='k',
             label="_nolegend_")
    plt.plot(exp['fit_x'], exp['fit_y'], lw=1.5, color='k',
             label="_nolegend_")
    plt.axhline(ls=':', lw=1, color='k')
    plt.axvline(ls=':', lw=1, color='k')
    plt.ylabel("Change in connection weight (%)")
    plt.yticks(np.linspace(-0.5, 1.0, 4),
               np.linspace(-50, 100, 4).astype(int))
    plt.xlabel("Spike timing (ms)")
    plt.xticks(np.linspace(-0.1, 0.1, 5),
               np.linspace(-100, 100, 5).astype(int))
    plt.axis((-0.1, 0.1, -0.85, 1.15))
    plt.legend(loc=2, prop={'size': 12})
    plt.tight_layout()
    plt.savefig('%s/fig1-bcm-stdp.pdf' % figuredir)
    print "Saved fig1-bcm-stdp.pdf"
    plt.close()


def plot_frequencies(sim, exp):
    plt.figure(figsize=(4.5, 3.5))
    plt.title('Frequency dependence of STDP')
    
    ax = plt.subplot(111)
    ax.set_xscale('log')

    plt.errorbar(sim['pulse_rates'], sim['low_m'],
                 yerr=[sim['low_m'] - sim['low_l'],
                       sim['low_h'] - sim['low_m']],
                 marker='o', color='0.6', lw=1.5,
                 label="Low activity (simulation)")

    plt.errorbar(exp['x_dark'], exp['y_dark'], yerr=exp['err_dark'],
                 marker='o', color='0.6', lw=1.5, mfc='w', ls='--',
                 label="Low activity (experiment)")

    plt.errorbar(sim['pulse_rates'], sim['high_m'],
                 yerr=[sim['high_m'] - sim['high_l'],
                       sim['high_h'] - sim['high_m']],
                 marker='o', color='k', lw=1.5,
                 label="High activity (simulation)")

    plt.errorbar(exp['x_light'], exp['y_light'], yerr=exp['err_light'],
                 marker='o', color='k', lw=1.5, mfc='w', ls='--',
                 label="High activity (experiment)")

    plt.axhline(linestyle='--', lw=1, color='k')
    plt.ylabel("Change in connection weight (%)")
    plt.xlabel("Stimulation frequency (Hz)")
    plt.yticks(np.linspace(-0.2, 0.2, 5),
               np.linspace(-20, 20, 5).astype(int))
    plt.xticks([1.0, 5.0, 10.0, 20.0, 50.0, 100.0],
               ['1','5','10','20','50','100'])
    plt.legend(loc=4, prop={'size': 11})
    plt.axis((0.7, 150.0, -0.22, 0.25))
    plt.tight_layout()
    plt.savefig('%s/fig2-bcm-stdp-frequency.pdf' % figuredir)
    print "Saved fig2-bcm-stdp-frequency.pdf"
    plt.close()


def simulate(theta, bcm_params, vary,
             trials=1, random_start=False, plot=None):
    # We either vary pulse_delay or pulse_rate
    # We can tell by what's in bcm_params
    if 'pulse_delay' in bcm_params.keys():
        varied = 'pulse_rate'
    elif 'pulse_rate' in bcm_params.keys():
        varied = 'pulse_delay'
    else:
        raise Exception("Expecting one of pulse_rate or pulse_delay in params")

    if random_start:
        start_omegas = np.random.standard_normal(
            (len(vary), trials))
    else:
        start_omegas = np.zeros((len(vary), trials))
    
    end_omegas = np.zeros_like(start_omegas)
    
    for i, v in enumerate(vary):
        for j in range(trials):
            params = bcm_params.copy()
            params[varied] = v
            sim = BCMSim(theta, start_omega=start_omegas[i][j], **params)
            sim.run()
            end_omegas[i][j] = sim.omega[-1]
            if plot is not None:
                sim.plot_activity('%s-pr%f' % (plot, pulse_rate))

    return end_omegas.squeeze()

# This is the data from Kirkwood, estimated via analyzing plots
exp_freq_data = {
    'x_light': [1.0, 10.0, 20.0, 100.0],
    'y_light': [-0.159, 0.049, 0.083, 0.209],
    'err_light': [0.034, 0.038, 0.025, 0.021],
    'x_dark': [1.0, 2.0, 10.0, 20.0, 100.0],
    'y_dark': [-0.06, -0.029, 0.155, 0.177, 0.198],
    'err_dark': [0.023, 0.045, 0.055, 0.03, 0.0],
}

# This is data from Bi \& Poo, estimated via analyzing plots
stdp_x = np.array([
        -0.0998, -0.0774, -0.0728, -0.0654, -0.0616, -0.0614, -0.0424,
        -0.0234, -0.0232, -0.0184, -0.0172, -0.0140, -0.0127, -0.0082,
        -0.0051, -0.0049, -0.0045, -0.0044, -0.0038, -0.0027, -0.0027,
        -0.0026,  0.0018,  0.0042,  0.0052,  0.0063,  0.0070,  0.0073,
         0.0074,  0.0078,  0.0079,  0.0080,  0.0081,  0.0167,  0.0168,
         0.0252,  0.0260,  0.0350,  0.0559,  0.0765,  0.0851,  0.0945])
stdp_y = np.array([
        -0.0173, -0.1468,  0.0301,  0.0068, -0.0804, -0.0073, -0.1377,
        -0.0928, -0.1510, -0.2365, -0.1377, -0.0463, -0.3204, -0.2564,
        -0.3577, -0.2190, -0.1327, -0.4366,  0.7625,  0.0027, -0.1593,
         0.2319,  0.9070,  0.3008,  1.0324,  0.2136,  0.3348,  0.9626,
         0.8480,  0.4926,  0.0193,  0.7334,  0.1945,  0.3564,  0.4386,
         0.1463,  0.0259,  0.1804, -0.1111,  0.0980, -0.0447,  0.0284])

stdp_fit_x, stdp_fit_y = BCMSim.fit_stdp_curve(stdp_x, stdp_y)
exp_stdp = {
    'x': stdp_x,
    'y': stdp_y,
    'fit_x': stdp_fit_x,
    'fit_y': stdp_fit_y,
}

if __name__ == '__main__':
    #
    # Recreate STDP curve
    #
    theta = 51

    curveparams = {
        'tau_pre': 0.01,
        'tau_post': 0.01,
        'pulse_rate': 5.0,
    }
    
    # Iterate over some pulse_delay values
    pulse_delays = np.linspace(-0.1, 0.1, 100)

    omegas = simulate(theta, curveparams, pulse_delays)[::-1]
    omegas /= np.amax(omegas)  # normalize

    sim_curve_x, sim_curve_y = BCMSim.fit_stdp_curve(pulse_delays, omegas)

    sim_stdp = {
        'x': pulse_delays,
        'y': omegas,
        'fit_x': sim_curve_x,
        'fit_y': sim_curve_y,
    }

    plot_stdp_curves(sim_stdp, exp_stdp)
    
    #
    # Recreate frequency effects
    #
    freqparams = {
        'tau_pre': 0.36,
        'tau_post': 0.0022,
        'pulse_delay': 0.00135,
        'num_pairings': 5,
    }

    theta_low = 197
    theta_high = 216
    pulse_rates = [1.0, 2.0, 10.0, 20.0, 100.0]

    np.random.seed(6)  #1, 5
    
    low_omegas = simulate(theta_low, freqparams, pulse_rates,
                          trials=25, random_start=True)
    low_scale = 0.2 / np.mean(low_omegas[-1])
    low_omegas *= low_scale
    low_conf = ci(low_omegas, axis=1)

    high_omegas = simulate(theta_high, freqparams, pulse_rates,
                           trials=25, random_start=True)
    high_scale = 0.2 / np.mean(high_omegas[-1])
    high_omegas *= high_scale
    high_conf = ci(high_omegas, axis=1)

    sim_freq_data = {
        'pulse_rates': pulse_rates,
        'low_l': low_conf[0],
        'low_m': np.mean(low_omegas, axis=1),
        'low_h': low_conf[1],
        'high_l': high_conf[0],
        'high_m': np.mean(high_omegas, axis=1),
        'high_h': high_conf[1],
    }

    plot_frequencies(sim_freq_data, exp_freq_data)
