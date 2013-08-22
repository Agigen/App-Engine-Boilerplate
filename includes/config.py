#!/usr/bin/env python

import os
from google.appengine.api import app_identity
import includes.exceptions

version = os.environ['CURRENT_VERSION_ID']

facebook_app_id = 'xxxxx'
facebook_app_secret = 'xxxxx'
google_analytics_id = 'UA-xxxxxx'

base_url = 'http://www.example.com'

is_devenv = False

if os.environ['SERVER_SOFTWARE'].startswith('Development'):
    is_devenv = True
    base_url = 'http://localhost:9999'
    google_analytics_id = 'UA-xxxxxx'
