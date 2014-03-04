#!/usr/bin/env python

import os
from google.appengine.api import app_identity
from google.appengine.ext import ndb

version = os.environ['CURRENT_VERSION_ID']

facebook_locale = 'en_US'
facebook_app_id = None
facebook_app_secret = None
google_analytics_id = None
google_universal_analytics_id = None


host = '%s.appspot.com' % app_identity.get_application_id()
base_url = 'http://%s' % host

is_devenv = False
secure_cookie = True

#error_email = 'errors@example.com'
#error_email = 'Boilderplate Errors <errors@example.com>'
error_email = None

if os.environ['SERVER_SOFTWARE'].startswith('Development'):
    is_devenv = True
    secure_cookie = False

    host = 'localhost:8080'
    base_url = 'http://%s' % host

    facebook_app_id = None
    facebook_app_secret = None
    google_analytics_id = None

    error_email = None


class SecretKey(ndb.Model):
    secret = ndb.StringProperty()

def _generate_secret_key():
    return os.urandom(16).encode("hex")

@ndb.transactional
def secret_key(key_name='site'):
    key = ndb.Key(SecretKey, key_name)
    ent = key.get()
    if not ent:
        ent = SecretKey(key=key, secret=_generate_secret_key())
        ent.put()

    return str(ent.secret)
