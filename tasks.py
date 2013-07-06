from invoke import run, task

# from scripts.download_results import download_all


resultsdir = "results/"

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
def sim(simfile, args=""):
    run("scripts/nengo-cl.sh " + simfile + " " + args, echo=True)
