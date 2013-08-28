#!/usr/bin/env python

import os
from google.appengine.api import app_identity
import includes.exceptions

version = os.environ['CURRENT_VERSION_ID']

facebook_app_id = None
facebook_app_secret = None
google_analytics_id = None


host = 'www.example.com'
base_url = 'http://%s' % host

is_devenv = False

if os.environ['SERVER_SOFTWARE'].startswith('Development'):
    is_devenv = True

    host = 'localhost:8080'
    base_url = 'http://%s' % host

    facebook_app_id = None
    facebook_app_secret = None
    google_analytics_id = None
