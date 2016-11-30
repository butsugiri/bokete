# -*- coding: utf-8 -*-
"""
ブラウザからキャプション(orボケ)
学習したモデルと，次元などの設定はコマンドライン引数から与えることにする．
TODO: ランディングページからのモデル選択 → やらないことにした
"""
import json
import os.path
import argparse
from cross_domain import crossdomain
from flask import Flask
from flask import request
from flask import render_template, url_for
from flask import send_from_directory, flash, redirect
from img2seq import GenerateBoke
from img2seq import Resource
from img2seq import ImageProcessor
from img2seq import DataProcessor
from flask_cors import CORS

from itertools import islice
from werkzeug.utils import secure_filename
from pymongo import MongoClient

# argparse
parser = argparse.ArgumentParser(description="BokeBoke")
parser.add_argument('-c', '--config', dest='config',
                    default="../config/toy.json", type=str, help='path to configuration file')
parser.add_argument('--model',
                    required=True, type=str, help='path to model file')
args = parser.parse_args()
config = Resource(args.config, train=False).config
model_path = args.model
gen = None

# MongoDB Connection
CLIENT = MongoClient()
DB = CLIENT["kiyono_bokete_data"]
COLLECTION = DB["boke"]

# initiate app
app = Flask(__name__)
CORS(app)

# app configuration
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config["image_static_path"] = config["image_path"]
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "HOGE"


# uploadされたファイルが画像かどうか判定する
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_boke_from_dataset(img_url):
    boke = [(x["boke"], int(x["star"])) for x in COLLECTION.find({"image_url": img_url})]
    return sorted(boke, key=lambda x: x[1], reverse=True)[:5]


# 以下，API endpoints
@app.route("/")
def index():
    if gen is None:
        return render_template("index.html")
    else:
        return render_template("index.html")


@app.route("/check")
def check():
    return render_template("check.html")


@app.route("/playground", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_path = url_for('uploaded_file', filename=filename)
            return json.dumps({'file_path': file_path})
    return render_template("playground.html")


@app.route("/from-dataset", methods=['POST'])
@crossdomain(origin='*')
def generate():
    posted_data = json.loads(request.data)
    # data_type = request.json["datatype"]
    # i = request.json["count"]
    data_type = posted_data["datatype"]
    i = posted_data["count"]
    if data_type == "train":
        data_source = config["train_data"]
    else:
        data_source = config["dev_data"]
    out = []
    with open(data_source) as fi:
        start = i * 2
        stop = (i + 1) * 2
        for line in islice(fi, start, stop):
            data = json.loads(line)
            # 自前でホスティングするならコレ
            # img_src = url_for('custom_static', filename=img)

            img = data["images"][0]["path"]
            boke = gen.generate_from_path(
                os.path.join(config["image_path"], img))
            img_src = data["images"][0]["url"]
            dataset_bokes = get_boke_from_dataset(img_src)  # bokes included in original dataset (5 bokes)
            out.append({
                "img_src": img_src,
                "boke": boke,
                "dataset_bokes": dataset_bokes
            })
    return json.dumps(out, ensure_ascii=False)


@app.route("/fromimage", methods=['POST'])
def image():
    posted_data = json.loads(request.data)
    image_path = posted_data["src"]
    img_name = os.path.basename(image_path)
    img_path = os.path.join("./uploads/", img_name)
    img_array = ImageProcessor(img_path).prepare()
    out = {"boke": gen.generate_from_array(img_array)}
    return json.dumps(out, ensure_ascii=False)


@app.route("/data-stats")
def get_data_stats():
    data = DataProcessor(config)
    stats = data.data_stats()
    print stats
    return json.dumps(stats)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/cdn/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.config['image_static_path'], filename)


@app.route("/reload-model")
def reload_model():
    global gen
    gen = GenerateBoke(model_path, config)
    gen.load_vocabulary()
    gen.setup_model()
    return json.dumps("success")


@app.route("/is-model-loaded")
def is_model_loaded():
    if gen is None:
        return json.dumps(False)
    else:
        return json.dumps(True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
