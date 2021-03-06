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
from PIL import Image
import settings
import imagehash
import requests
import datetime
import time
import calendar


def snooze():
    """Snooze the job."""
    url = '%s/api/task?api_key=%s' % (settings.SERVER_NAME,
                                      settings.APIKEY)
    res = requests.get(url)

    if (res.status_code == 429):
        print "we have to wait"
        remaining = (int(res.headers['X-RateLimit-Reset']) -
                     calendar.timegm(time.gmtime()))
        time.sleep(remaining + 120)


def create_task(pbclient, **kwargs):
    """Create a task."""

    snooze()

    if kwargs.get('Create_time') is None:
        now = datetime.datetime.utcnow().isoformat()
        kwargs['Create_time'] = now

    info = dict(title=kwargs['filename'],
                link_raw=kwargs['url'],
                filename=kwargs['filename'],
                url_m=kwargs['url'],
                link=kwargs['url'],
                url_b=kwargs['url'],
                cameraID=kwargs['camera_id'],
                email_from="File Uploader",
                email_subject="File Uploader",
                email_date="File Uploader",
                image=kwargs['url'],
                ahash=kwargs['ahash'],
                video=kwargs['video_url'],
                isvideo=kwargs['isvideo'],
                content_type=kwargs['content_type'],
                Create_time=kwargs['Create_time'],
                deploymentLocationID=kwargs['deploymentLocationID'])
    return pbclient.create_task(kwargs['project_id'],
                                n_answers=5,
                                info=info)


def get_ahash(data):
    """Generates image ahash."""
    img = Image.open(data)
    ahash = str(imagehash.average_hash(img))
    return ahash


def check_exists(data):
    """Check if exists already."""

    snooze()

    ahash = get_ahash(data)
    query = 'ahash::%s' % ahash
    url = settings.SERVER_NAME + '/api/task'
    params = dict(api_key=settings.APIKEY,
                  info=query,
                  fulltextsearch=1,
                  all=1)
    res = requests.get(url, params=params)
    print res.json()
    if len(res.json()) >= 1:
        task = res.json()[0]
        return True, ahash, task
    else:
        return False, ahash, None
