import sys
from os import walk
import imghdr
import csv
import argparse
import os
from flask import Flask, redirect, url_for, request
from flask import render_template
from flask import send_file
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      app.config["path_of_image_to_annotate"]=secure_filename(f.filename)
      f.save("images/"+secure_filename(f.filename))
      return redirect(url_for("tagger"))

@app.route('/tagger')
def tagger():

    directory = app.config['IMAGES']
    labels = app.config["LABELS"]
    try:
        print("************************************",app.config["path_of_image_to_annotate"])
        print(directory)
    except:
        app.config["path_of_image_to_annotate"]="template.png"
    return render_template('tagger.html', directory=directory, image=app.config["path_of_image_to_annotate"], labels=labels)

@app.route('/next')
def next():
    image = app.config["path_of_image_to_annotate"]
    with open(app.config["OUT"],'a') as f:
        for label in app.config["LABELS"]:
            f.write(image + "," +
            label["id"] + "," +
            label["name"] + "," +
            str(round(float(label["xMin"]))) + "," +
            str(round(float(label["xMax"]))) + "," +
            str(round(float(label["yMin"]))) + "," +
            str(round(float(label["yMax"]))) + "\n")
    app.config["LABELS"] = []
    return redirect(url_for('tagger'))


@app.route('/add/<id>')
def add(id):
    xMin = request.args.get("xMin")
    xMax = request.args.get("xMax")
    yMin = request.args.get("yMin")
    yMax = request.args.get("yMax")
    app.config["LABELS"].append({"id":id, "name":"", "xMin":xMin, "xMax":xMax, "yMin":yMin, "yMax":yMax})
    return redirect(url_for('tagger'))

@app.route('/remove/<id>')
def remove(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    return redirect(url_for('tagger'))

@app.route('/label/<id>')
def label(id):
    name = request.args.get("name")
    app.config["LABELS"][int(id) - 1]["name"] = name
    return redirect(url_for('tagger'))

@app.route('/image/<f>')
def images(f):
    images = app.config['IMAGES']
    try:
        print("************************************",app.config["path_of_image_to_annotate"])
    except:
        app.config["path_of_image_to_annotate"]="template.png"
    return send_file(os.path.join(images,app.config["path_of_image_to_annotate"]))


if __name__ == "__main__":
    app.config['IMAGES']="./images"
    app.config["LABELS"] = []
    app.config["OUT"] = "out.csv"
    with open("out.csv",'w') as f:
        f.write("image,id,name,xMin,xMax,yMin,yMax\n")
    app.run(debug="True")







































