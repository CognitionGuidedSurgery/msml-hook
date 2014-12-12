__author__ = 'weigl'

from flask import Flask, request
import json
import pprint
import multiprocessing

app = Flask(__name__)

queue = multiprocessing.Queue()

@app.route("/msml/", methods=["POST"])
def hook():
    queue.put_nowait(request.json)
    return "Job enqueud"

def start_dispatcher():
    process = multiprocessing.Process(target=wait_incoming, args=(queue,))
    process.start()

def wait_incoming(queue):
    print "dispatcher started"
    pool = multiprocessing.Pool(2)

    while True:
        data = queue.get()
        try:
            name = data['repository']['name']
            repository = data['repository']['clone_url']
            commit  = data['after']

            p = pool.Process(target=execute, args=(name, repository, commit))
            p.start()

        except BaseException as e:
            print e.message


import tempfile
import os
import yaml
import msml.frontend

def execute(name, repository, commit):
    os.chdir("/tmp")
    os.system("git clone %s %s" % (repository, name))
    os.chdir(name)
    os.system("git checkout %s" % commit)

    with open("msml.yaml") as fp:
        execdata = yaml.safe_load(fp)

    for sc in execdata['scenarios']:
        fil = sc['file']

        for setting in sc['settings']:
            exporter = setting['exporter']
            odir = setting['outputdir']


            try:
                print "Exec MSML: %s, %s, %s" % (fil, exporter, odir)
                app = msml.frontend.App(files=(fil,), exporter=exporter, output_dir=odir)
                app.execute_msml_file("/tmp/%s/%s" %(name,fil))
            except BaseException as e:
                print e.message
