#!/usr/bin/env python
# coding=utf8

import webapp2
import time
import json
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from controllers import application


# EXAMPLE
# This is how you get a upload URL for your template. Use in controller that
# renders the template for your file upload form.
# upload_url = blobstore.create_upload_url(webapp2.uri_for('admin-file-upload'))

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        saved_file_keys = []
        for f in self.get_uploads():
            saved_file_keys.append(f.key())

        self.response.headers['Content-Type'] = 'application/json'
        self.data = {'files': [str(blob_key) for blob_key in saved_file_keys]}
        self.status = 'ok'
        self.response.out.write(json.dumps({
            'status': self.status.lower(),
            'time': time.time(),
            'data': self.data
        }))
