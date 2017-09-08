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
import os
import settings
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key

def upload_to_s3(file):
    con = S3Connection(settings.AWS_ACCESS_KEY,
                       settings.AWS_SECRET_KEY)
    bucket = con.get_bucket(settings.S3_BUCKET)
    bucket.set_acl('public-read')
    s3_filelocation = os.path.join(settings.S3_FOLDER, file)
    local_file = os.path.join(settings.UPLOAD_DIR, file)
    k = Key(bucket)
    k.key = s3_filelocation
    k.set_contents_from_filename(local_file)
    k.set_acl('public-read')
    url = k.generate_url(expires_in=0, query_auth=False)
    return url
