from flask import Flask, request, jsonify, render_template
from flask import send_from_directory, redirect, url_for
from werkzeug import secure_filename
import os
import settings


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return jsonify('No file part')
    file = request.files['file']
    if file.filename == '':
        return jsonify('No file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(settings.UPLOAD_DIR, filename))
        return jsonify(dict(status='ok'))

if __name__ == '__main__': # pragma: no cover
    app.debug = True
    app.run()
