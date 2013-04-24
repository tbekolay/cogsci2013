try:
    import requests
except:
    print ("Requires requests. Please apt-get install python-requests,"
           " or pip install requests.")
    import sys
    sys.exit()

import json
import os
import zipfile


resultsdir = "results/"

def download_all(article_id, outdir, unzip=False):
    r = requests.get("http://api.figshare.com/v1/articles/" + article_id)
    detail = json.loads(r.content)
    for file_info in detail['items'][0]['files']:
        outpath = os.path.join(outdir, file_info['name'])
        if os.path.exists(outpath):
            print outpath + " exists. Skipping."
            continue
        with open(outpath, 'wb') as outf:
            print "Downloading " + outpath + "..."
            dl = requests.get(file_info['download_url'])
            outf.write(dl.content)
        if unzip and zipfile.is_zipfile(outpath):
            print "Unzipping " + outpath + "..."

            with zipfile.ZipFile(outpath) as zf:
                zf.extractall(outdir)
            os.remove(outpath)

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
