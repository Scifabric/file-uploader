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

def create_task(pbclient, project_id, data, isvideo, **kwargs):
    """Create a task."""

    # info = dict(title=timestamped_filename,
    #             link_raw=url,
    #             filename=timestamped_filename,
    #             url_m=url,
    #             link=url,
    #             url_b=url,
    #             email_from=task['email_from'],
    #             email_subject=task['email_subject'],
    #             email_date=task['email_date'],
    #             image=url,
    #             video=video_url,
    #             isvideo=task['isvideo'],
    #             content_type=task['content_type']
    #                     )

def check_exists(data):
    """Check if exists already."""
    img = Image.open(data)
    ahash = str(imagehash.average_hash(img))
    query = 'ahash::%s' % ahash
    url = settings.SERVER_NAME + '/api/task'
    params = dict(api_key=settings.APIKEY,
                  info=query,
                  fulltextsearch=1)
    response = requests.get(url, params=params)
    if len(response.json()) >= 1:
        return True
    else:
        return False
