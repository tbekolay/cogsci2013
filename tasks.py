import os.path
import shutil

from invoke import run, task

from scripts.download_results import download_all
from scripts.analysis.bcm import main as analyze_bcm
from scripts.analysis.bcm_nengo import main as analyze_bcm_nengo
from scripts.analysis.bcm_rule import main as analyze_bcm_rule
from scripts.analysis.learn_digits import main as analyze_digits
from scripts.analysis.learn_testing import main as analyze_learn
from scripts.analysis.sparsity import main as analyze_sparsity

thisdir = os.path.dirname(os.path.realpath(__file__))
nengodir = os.path.expanduser("~/nengo-latest/")
resultsdir = thisdir + "/results/"

@task
def dl_results():
    print "============"
    print "Experiment 1"
    print "============"
    download_all("155314", resultsdir + "bcm")

    print "========================="
    print "Experiment 2 optimization"
    print "========================="
    download_all("155525", resultsdir + "functions-optimize", unzip=False)

    print "============"
    print "Experiment 2"
    print "============"
    download_all("155606", resultsdir + "functions-test", unzip=False)

    print "============"
    print "Experiment 3"
    print "============"
    download_all("155317", resultsdir + "digits", unzip=True)

@task
def link_scripts():
    link_name = nengodir + "/trevor"
    if not os.path.exists(link_name):
        os.symlink(thisdir + "/scripts/nengo/", link_name)

@task
def sim(simfile, args=""):
    run("scripts/nengo-cl.sh " + simfile + " " + args, echo=True)

@task
def analyze(target='all', presentation=False):
    if target in ('all', 'sparsity'):
        analyze_sparsity()
        if presentation:
            shutil.copy2('figures/dense.svg',
                         '../cogsci2013-pres/img/dense.svg')
            shutil.copy2('figures/sparse.svg',
                         '../cogsci2013-pres/img/sparse.svg')
    if target in ('all', 'digits'):
        pass
        #analyze_digits()
    if target in ('all', 'bcm'):
        #analyze_bcm(presentation)
        #analyze_bcm_nengo(presentation)
        if presentation:
            analyze_bcm_rule()
            shutil.copy2('figures/bcm_rule.svg',
                         '../cogsci2013-pres/img/bcm_rule.svg')
            #shutil.copy2('figures/fig1-bcm-stdp.svg',
            #             '../cogsci2013-pres/img/stdp.svg')
            #shutil.copy2('figures/fig2-bcm-stdp-frequency.svg',
            #             '../cogsci2013-pres/img/freq.svg')
            #shutil.copy2('figures/fig3-bcm.svg',
            #             '../cogsci2013-pres/img/sparsity.svg')
    if target in ('all', 'learn'):
        analyze_learn(presentation)
        if presentation:
            shutil.copy2('figures/channel-learncurve-pes.svg',
                         '../cogsci2013-pres/img/tr-learncurve-pes.svg')
            shutil.copy2('figures/conv-learncurve-pes.svg',
                         '../cogsci2013-pres/img/learncurve-pes.svg')
            shutil.copy2('figures/channel-learncurve.svg',
                         '../cogsci2013-pres/img/tr-learncurve.svg')
            shutil.copy2('figures/conv-learncurve.svg',
                         '../cogsci2013-pres/img/learncurve.svg')
            #shutil.copy2('figures/fig5-param-boxplot.svg',
            #             '../cogsci2013-pres/img/params.svg')
