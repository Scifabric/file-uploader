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
from PIL import Image
from flask import Flask, request, jsonify, render_template, json
from flask import send_from_directory, redirect, url_for, session
from werkzeug import secure_filename
from piexif._exceptions import InvalidImageDataError
from s3 import upload_to_s3
from video import handle_video
from tasks import check_exists, create_task
from redis import Redis
from rq import Queue
from rq.queue import FailedQueue
from jobs import async_upload
from flask_socketio import SocketIO, send, emit, join_room, leave_room

app = Flask(__name__)

socketio = SocketIO(app)

q = Queue(connection=Redis())
fq = FailedQueue(connection=Redis())

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
    if settings.PUBLISHED:
        projects = pbclient.find_project(api_key=settings.APIKEY,
                                         all=1, published=True,
                                         limit=100)
    else:
        projects = pbclient.find_project(api_key=settings.APIKEY,
                                         all=1,
                                         limit=100)
    data = [project.__dict__['data'] for project in projects]
    return jsonify(data)


@app.route('/upload', methods=['POST'])
def upload():
    project_id = request.form['project_id']
    project_name = request.form['project_name']
    camera_id = request.form['camera_id'] or None
    deploymentLocationID = request.form['deploymentLocationID']
    duplicates = request.form['duplicates']
    room = request.form['room']
    if deploymentLocationID is None or deploymentLocationID == '':
        deploymentLocationID = project_name
    if 'file' not in request.files:
        flash('No file part')
        return jsonify('No file part')
    file = request.files['file']
    if file.filename == '':
        return jsonify('No file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not os.path.exists(settings.UPLOAD_DIR):
            os.makedirs(settings.UPLOAD_DIR)
        path = os.path.join(settings.UPLOAD_DIR, filename)
        file.save(path)

        kwargs = dict(project_id=project_id,
                      project_name=project_name,
                      camera_id=camera_id,
                      deploymentLocationID=deploymentLocationID,
                      filename=filename,
                      path=path,
                      room=room,
                      duplicates=duplicates)
        job = q.enqueue(async_upload, timeout=15*60, **kwargs)
        return jsonify({'jobId': job.id})
    else:
        return "ERROR"


@app.route('/jobstatus')
def completed():
    pending = []
    completed = []
    error = []
    job_ids = r.get('file-uploader-jobs')
    if job_ids:
        jobs = json.loads(job_ids)
        for jobID in jobs:
            job = q.fetch_job(jobID)
            if (job.result):
                completed.append(job.result)
            else:
                pending.append(job.id)
    failed = fq.get_jobs()
    for f in failed:
        error.append(f.id)
    res = dict(pending=pending,
               completed=completed,
               error=error)
    return jsonify(res)


@socketio.on('jobcompleted')
def handle_job_completed(data):
    print('Job COMPLETED ' + str(data))
    emit('jobStatus', data, room=data['room'])


@socketio.on('join')
def handle_join(data):
    join_room(data['room'])
    print("User joined room %s" % data['room'])


@socketio.on('leave')
def handle_join(data):
    leave_room(data['room'])


if __name__ == '__main__':  # pragma: no cover
    app.debug = True
    # app.run()
    socketio.run(app)
