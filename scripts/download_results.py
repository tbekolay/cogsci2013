try:
    import requests
except:
    print ("Requires requests. Please apt-get install python-requests,"
           " or pip install requests.")
    raise

import json
import os
import zipfile


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

