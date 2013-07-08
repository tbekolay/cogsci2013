import os.path

from invoke import run, task

from scripts.download_results import download_all
from scripts.analysis.learn_digits import main as analyze_digits

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
def analyze(target='all'):
    if target in ('all', 'digits'):
        analyze_digits()
