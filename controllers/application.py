#!/usr/bin/env python

import json
import traceback
import logging
import datetime
import webapp2
import time

from webapp2_extras import jinja2
from webapp2_extras import sessions
from webapp2_extras import sessions_ndb

from google.appengine.api import mail
from google.appengine.api import users

from includes import exceptions
from includes import config


def jinja2_factory(app):
    j = jinja2.Jinja2(app, config={'environment_args':{'autoescape':False}})
    j.environment.filters.update({
        'json': lambda a: json.dumps(a),
        'ng': lambda a: "{{%s}}" % a
    })
    j.environment.globals.update({
        'config': config,
        'uri_for': webapp2.uri_for
    })
    return j

def report_error(request):
    if config.error_email:
        try:
            mail.send_mail(
                sender="%s error reporter <error@%s.appspotmail.com>" % (config.app_identity.get_application_id(), config.app_identity.get_application_id()),
                to=config.error_email,
                subject="%s: %s has encountered an unhandled exception" % (str(datetime.datetime.now()), config.app_identity.get_application_id()),
                body="Unhandled exception (%s):\n %s" % (request.path_qs, traceback.format_exc()))
        except Exception, e:
            logging.error('Could not send email about error: %s' % str(e))


class BaseHandler(webapp2.RequestHandler):
    def head(self, *args, **kwargs):
        pass

    def initialize(self, request, response):
        request.charset = 'utf-8'
        super(BaseHandler, self).initialize(request, response)

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        if not config.public and not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.path));
            return

        try:
            # Dispatch the request.
            super(BaseHandler, self).dispatch()
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session(
            factory=sessions_ndb.DatastoreSessionFactory)

    @webapp2.cached_property
    def user(self):
        return users.get_current_user()


class RequestHandler(BaseHandler):
    require_roles = []

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(factory=jinja2_factory, app=self.app)

    def render_template(self, template, data):
        data.update({
            'request_path': self.request.path,
            'user': self.user
        })

        return self.jinja2.render_template(template, **data)

    def dispatch(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.data = {}
        self.template = None

        return_value = super(RequestHandler, self).dispatch()

        if self.template:
            self.response.out.write(self.render_template(self.template, self.data))

        return return_value

    def handle_exception(self, exception, debug_mode):
        self.response.clear()

        if isinstance(exception, exceptions.APIError):
            getattr(logging, exception.loglevel)("API exception:\n%s" % traceback.format_exc())
            self.response.set_status(exception.http_status, exception.human_message)
            if isinstance(exception, exceptions.NoSuchEntityError):
                self.template = '404.html'
            if isinstance(exception, exceptions.PermissionDeniedError):
                self.template = '403.html'
            else:
                self.template = '500.html'
        elif isinstance(exception, ValueError):
            logging.info("ValueError:\n%s" % traceback.format_exc())
            self.response.set_status(400, "Invalid Parameter")

            self.template = '400.html'
        else:
            logging.warning("Unhandled exception: %s" % traceback.format_exc())
            self.response.set_status(500, "Internal Server Error")

            report_error(self.request)

            self.template = '500.html'


class APIRequestHandler(BaseHandler):
    def dispatch(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.status = 'ok'
        self.data = {}

        return_value = super(APIRequestHandler, self).dispatch()
        self.response.out.write(json.dumps({
            'status': self.status.lower(),
            'time': time.time(),
            'data': self.data
        }))
        return return_value

    def handle_exception(self, exception, debug_mode):
        self.response.clear()

        no_response_codes = self.request.get('suppress_response_codes', None)
        if isinstance(exception, exceptions.APIError):
            getattr(logging, exception.loglevel)("API exception:\n%s" % traceback.format_exc())
            if not no_response_codes:
                self.response.set_status(exception.http_status, exception.human_message)
            self.status = exception.json_message
        elif isinstance(exception, ValueError):
            logging.info("ValueError:\n%s" % traceback.format_exc())
            if not no_response_codes:
                self.response.set_status(400, "Invalid parameter")
            self.status = 'ERROR_INVALID_PARAMETER'
        else:
            logging.error("Unhandled exception:\n%s" % traceback.format_exc())
            if not no_response_codes:
                self.response.set_status(500)

            report_error(self.request)

            self.status = 'ERROR_INTERNAL_FAILURE'
