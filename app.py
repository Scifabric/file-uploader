# -*- coding: utf8 -*-
# This file is part of PYBOSSA.
#
# Copyright (C) 2017 Scifabric LTD.
#
# PYBOSSA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PYBOSSA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PYBOSSA.  If not, see <http://www.gnu.org/licenses/>.
import magic
import os
import pbclient
import settings
import piexif
from flask import Flask, request, jsonify, render_template, json
from flask import send_from_directory, redirect, url_for
from werkzeug import secure_filename
from piexif._exceptions import InvalidImageDataError
from s3 import upload_to_s3
from video import handle_video
from tasks import check_exists, create_task

app = Flask(__name__)


pbclient.set('api_key', settings.APIKEY)
pbclient.set('endpoint', settings.SERVER_NAME)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS

@app.route('/projects')
def projects():
    projects = pbclient.find_project(api_key=settings.APIKEY,
                                     all=1, published=True,
                                     limit=100)
    data = [project.__dict__['data'] for project in projects]
    return jsonify(data)

@app.route('/upload', methods=['POST'])
def upload():
    project_id = request.form['project_id']
    camera_id = request.form['camera_id']
    print project_id, camera_id
    if 'file' not in request.files:
        flash('No file part')
        return jsonify('No file part')
    file = request.files['file']
    if file.filename == '':
        return jsonify('No file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(settings.UPLOAD_DIR, filename)
        file.save(path)
        mime = magic.from_file(path, mime=True)
        isvideo = True
        if 'image' in mime:
            isvideo = False
        exif = 'removed'
        if isvideo:
            video_url, thumbnail_url = handle_video(filename)
            tmp = dict(project_id=project_id,
                       filename=filename,
                       url=thumbnail_url,
                       video_url=video_url,
                       isvideo=True,
                       content_type="video/mp4")
            task = create_task(pbclient,**tmp)
        else:
            try:
                piexif.remove(path)
            except InvalidImageDataError:
                exif = 'This image types does not support EXIF'
            if check_exists(path) is False:
                data_url = upload_to_s3(path, filename)
                tmp = dict(project_id=project_id,
                           filename=filename,
                           url=data_url,
                           video_url=None,
                           isvideo=False,
                           content_type=mime)
                task = create_task(pbclient,**tmp)
        # Check if the image has been already uploaded
        return jsonify(dict(status='ok', exif=exif,
                            task=task.__dict__['data']))


if __name__ == '__main__':  # pragma: no cover
    app.debug = True
    app.run()
