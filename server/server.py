import os
import googlenet.test_ps
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, jsonify, Response
from werkzeug.utils import secure_filename
import multiprocessing
from flask_cors import CORS, cross_origin

UPLOAD_FOLDER = os.path.join(os.getcwd(), "upload/")
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])

app = Flask(__name__)
cors = CORS(app, resources={r"/upload": {"origins": "http://localhost:8000"}})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_to_googlenet(file_url, return_list):
    googlenet.test_ps.pass_url_to_graph(file_url, return_list)

# only handles passing one argument
def spawn_process(func, arg):
    manager = multiprocessing.Manager()
    return_list = manager.list()
    p = multiprocessing.Process(target=func, args=(arg,return_list))
    p.start()
    p.join()
    return return_list

# uploading route, using a default set of file types
@app.route("/upload", methods = ["GET", "POST"])
@cross_origin(origin='localhost', headers=['Content- Type'])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "There was no file in the request."
        file_uploaded = request.files["file"]
        filename = secure_filename(file_uploaded.filename)
        if filename == "":
            return "Please upload a file."
        if file_uploaded and allowed_file(file_uploaded.filename):
            file_uploaded.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploaded_file_url = str(request.base_url) + "/" + str(filename)
            probabilities = spawn_process(send_to_googlenet, uploaded_file_url)
            #probabilities = ["string1", "string2", "string3"]
            toprint = "<br>".join(probabilities)
            return jsonify({'key':toprint}), 200

# redirect to uploaded file
@app.route('/upload/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.secret_key = "jimmy rustle"
    app.config['SESSION_TYPE'] = "filesystem"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.run()
