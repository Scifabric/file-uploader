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
import sh
import os
import sys
import tempfile
import settings
from s3 import upload_to_s3


def handle_video(filename):
    """Handle video."""
    outputvideo = tempfile.NamedTemporaryFile(delete=False)
    thumbnail = tempfile.NamedTemporaryFile(delete=False)
    try:
        outputvideo.close()
        # generate mp4 container data
        path = os.path.join(settings.UPLOAD_DIR, filename)
        print(sh.ffmpeg('-y',
                        '-i', path,
                        '-c', 'copy',
                        '-f', 'mp4',
                        outputvideo.name))
        # generate thumbnail
        # ffmpeg -ss 3 -i test.mp4 -vf "select=gt(scene\,0.4)" 
        # -frames:v 5 -vsync vfr -vf fps=fps=1/600 out%02d.jpg
        print(sh.ffmpeg('-ss', '3', '-i', path, '-vf',
                        '"select=gt(scene\,0.4)"', '-frames:v',
                        '5', '-vsync', 'vfr', '-vf',
                        'fps=fps=1/600', '-y', '-f',
                        'mjpeg', thumbnail.name))
        mp4_filename = filename.split('h264')[0] + 'mp4'
        upload_to_s3(outputvideo.name, mp4_filename)
        upload_to_s3(thumbnail.name, mp4_filename + '.jpg')
    except:
        raise
    finally:
        os.remove(outputvideo.name)
        os.remove(thumbnail.name)
