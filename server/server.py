import os
import googlenet.test_ps
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.getcwd(), "upload/")
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_to_googlenet(file_url):
    googlenet.test_ps.pass_url_to_graph(file_url)
    return None

# uploading route, using a default set of file types
@app.route("/upload", methods = ["GET", "POST"])
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
            uploaded_file_url = str(request.base_url) + str(filename)
            send_to_googlenet(uploaded_file_url)
            return "{0} successfully uploaded.".format(filename)

# redirect to uploaded file
@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.secret_key = "jimmy rustle"
    app.config['SESSION_TYPE'] = "filesystem"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.run()
