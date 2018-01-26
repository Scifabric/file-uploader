import magic
import os
import pbclient
import settings
import piexif
from PIL import Image
from flask import Flask, request, jsonify, render_template, json
from flask import send_from_directory, redirect, url_for
from werkzeug import secure_filename
from piexif._exceptions import InvalidImageDataError
from s3 import upload_to_s3
from video import handle_video
from tasks import check_exists, create_task
from redis import Redis
from rq import Queue
from socketIO_client import SocketIO

pbclient.set('api_key', settings.APIKEY)
pbclient.set('endpoint', settings.SERVER_NAME)


def async_upload(**kwargs):
    sio = SocketIO(settings.SOCKETIO_SERVER, settings.SOCKETIO_PORT)
    project_id = kwargs['project_id']
    project_name = kwargs['project_name']
    camera_id = kwargs['camera_id']
    deploymentLocationID = kwargs['deploymentLocationID']
    filename = kwargs['filename']
    path = kwargs['path']
    room = kwargs['room']
    duplicates = kwargs['duplicates']

    with open(path) as file:
        mime = magic.from_file(path, mime=True)
        isvideo = True
        if 'image' in mime:
            isvideo = False
        if isvideo:
            video_url, thumbnail_url = handle_video(filename)
            tmp = dict(project_id=project_id,
                       filename=filename,
                       url=thumbnail_url,
                       video_url=video_url,
                       isvideo=True,
                       camera_id=camera_id,
                       ahash=None,
                       content_type="video/mp4",
                       deploymentLocationID=deploymentLocationID)
            task = create_task(pbclient, **tmp)
            return jsonify(dict(status='ok', exif=None,
                                task=task.__dict__['data']))
        else:
            try:
                # Get from Exif DateTimeOriginal
                exif_dict = piexif.load(path)
                exif_dict.pop('thumbnail')
                data_d = {}
                for ifd in exif_dict:
                    data_d[ifd] = {
                        piexif.TAGS[ifd][tag]["name"]: exif_dict[ifd][tag]
                        for tag in exif_dict[ifd]}
                # Resize file to settings size
                thumbnail = Image.open(file)
                thumbnail.thumbnail(settings.THUMBNAIL)
                thumbnail.save(path)
                exif = 'removed'
                piexif.remove(path)
                Create_time = data_d['Exif']['DateTimeOriginal']
            except InvalidImageDataError:
                exif = 'This image types does not support EXIF'
                Create_time = None
            except KeyError:
                exif = 'This image types does not support EXIF'
                Create_time = None

            image_exists, ahash, task = check_exists(path)

            if duplicates == 'No':
                image_exists = False

            if image_exists is False:
                data_url = upload_to_s3(path, filename)
                tmp = dict(project_id=project_id,
                           filename=filename,
                           url=data_url,
                           video_url=None,
                           isvideo=False,
                           camera_id=camera_id,
                           ahash=ahash,
                           content_type=mime,
                           Create_time=Create_time,
                           deploymentLocationID=deploymentLocationID)
                task = create_task(pbclient, **tmp)
                final = dict(status='ok', exif=exif,
                             task=task.__dict__['data'],
                             room=room)
                sio.emit('jobcompleted', final)
                return final
            else:
                final = dict(status='ok', exif=exif,
                             task=task,
                             room=room)
                sio.emit('jobcompleted', final)
                return final
