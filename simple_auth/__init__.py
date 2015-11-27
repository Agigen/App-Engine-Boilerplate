#!/usr/bin/env python
#coding=utf8

import datetime
import webapp2
import logging
import hashlib
import urllib
import os
import json
from google.appengine.ext import ndb
import config

import controllers.application


SESSION_COOKIE_NAME = 'SIMPLE_AUTH_SSID'
LOGIN_PATH = '/login'

LIFETIME_SECS = 2592000


class Error(Exception):
    """General auth error"""


class Auth(ndb.Model):
    ssid = ndb.StringProperty(required=True)
    verified = ndb.BooleanProperty(default=False)
    created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
    accessed_at = ndb.DateTimeProperty(auto_now_add=True)

    def touch(self):
        now = datetime.datetime.now()
        if self.accessed_at < now - datetime.timedelta(seconds=300):
            self.accessed_at = now
            self.put()

    @classmethod
    def verify(cls, ssid):
        a = cls.get_by_id(ssid)
        if a:
            a.touch()
            return a.verified

        return False

    @classmethod
    def expired(cls):
        return cls.query(cls.accessed_at < (datetime.datetime.now() - datetime.timedelta(seconds=int(LIFETIME_SECS*1.2))))


def _generate_session_key():
    return os.urandom(128).encode("hex")


def check_auth(request_handler, *args, **kwargs):
    _is_local = config.application.simple_auth.get('except_devserver') \
                and os.environ['SERVER_SOFTWARE'].startswith('Development')
    ssid = request_handler.request.cookies.get(SESSION_COOKIE_NAME, None)
    if _is_local or ssid and Auth.verify(ssid):
        return True

    return request_handler.redirect('%s?%s' % (
        LOGIN_PATH,
        urllib.urlencode({'next': request_handler.request.uri})
        ))


def create_session(request_handler):
    ssid = _generate_session_key()
    a = Auth(
        id=ssid,
        ssid=ssid,
        verified=True
    )
    a.put()
    request_handler.response.set_cookie(SESSION_COOKIE_NAME,
                                        ssid,
                                        httponly=True,
                                        path="/",
                                        max_age=LIFETIME_SECS)


class LoginHandler(webapp2.RequestHandler):
    """Login request handler"""

    @webapp2.cached_property
    def jinja2(self):
        return controllers.application.jinja2.get_jinja2(factory=controllers.application.jinja2_factory, app=self.app)

    def get(self):
        """Show login page"""
        self.response.out.write(self.jinja2.render_template('simple_auth.html'))

    def post(self):
        """Handle login post"""
        if 'X-Requested-With' in self.request.headers:
            self.response.headers['Content-Type'] = 'application/json'

        if hashlib.md5(self.request.get('password')).hexdigest() in config.application.simple_auth.get('md5ed_passwords', []):
            # Create session and set cookie.
            create_session(self)
        else:
            if 'X-Requested-With' in self.request.headers:
                self.response.out.write(json.dumps({
                    'next': None,
                    'status': 'incorrect_password'
                }))
                return

        if 'X-Requested-With' in self.request.headers:
            self.response.out.write(json.dumps({
                'next': str(self.request.get('next', '/')),
                'status': 'ok'
            }))
            return
        else:
            self.redirect(str(self.request.get('next', '/')))
