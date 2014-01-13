#!/usr/bin/env python

import json
import traceback
import logging
import datetime
import webapp2

from webapp2_extras import jinja2

from google.appengine.api import mail
from google.appengine.api import users

import includes.exceptions
import includes.config

def jinja2_factory(app):
    j = jinja2.Jinja2(app, config={'environment_args':{'autoescape':False}})
    j.environment.filters.update({
        'json': lambda a: json.dumps(a)
    })
    j.environment.globals.update({
        'config': includes.config
    })
    return j

def report_error():
    if includes.config.error_email:
        try:
            mail.send_mail(
                sender="%s error reporter <error@%s.appspotmail.com>" % (includes.config.app_identity.get_application_id(), includes.config.app_identity.get_application_id()),
                to=includes.config.error_email,
                subject="%s: %s has encountered an unhandled exception" % (str(datetime.datetime.now()), includes.config.app_identity.get_application_id()),
                body="Unhandled exception: %s" % traceback.format_exc())
        except Exception, e:
            logging.error('Could not send email about error: %s' % str(e))

class RequestHandler(webapp2.RequestHandler):
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

    def initialize(self, request, response):
        request.charset = 'utf-8'
        super(RequestHandler, self).initialize(request, response)
        self.data = {}
        self.template = None

    def dispatch(self):
        return_value = super(RequestHandler, self).dispatch()
    
        if self.template:
            self.response.out.write(self.render_template(self.template, self.data))
    
        return return_value
    
    def handle_exception(self, exception, debug_mode):
        self.response.clear()
        
        if isinstance(exception, includes.exceptions.APIError):
            getattr(logging, exception.loglevel)("API exception:\n%s" % traceback.format_exc())
            self.response.set_status(exception.http_status, exception.human_message)
            if isinstance(exception, includes.Exceptions.NoSuchEntityError):
                self.template = '404.html'
            else:
                self.template = '500.html'
        elif isinstance(exception, ValueError):
            logging.info("ValueError:\n%s" % traceback.format_exc())
            self.response.set_status(400, "Invalid Parameter")

            self.template = '400.html'
        else:
            logging.warning("Unhandled exception: %s" % traceback.format_exc())
            self.response.set_status(500, "Internal Server Error")

            report_error()

            self.template = '500.html'
    
    @property
    def user(self):
        if not hasattr(self, 'current_user'):
            self.current_user = users.get_current_user()
        return self.current_user
    


class APIRequestHandler(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(APIRequestHandler, self).initialize(request, response)
        self.response.headers['Content-Type'] = 'application/json'
        self.data = {
            'status': 'ok',
        }
    
    def dispatch(self):
        return_value = super(APIRequestHandler, self).dispatch()
        self.response.out.write(json.dumps(self.data))
        return return_value
    
    def handle_exception(self, exception, debug_mode):
        self.response.clear()
        
        no_response_codes = self.request.get('suppress_response_codes', None)
        if isinstance(exception, includes.exceptions.APIError):
            getattr(logging, exception.loglevel)("API exception:\n%s" % traceback.format_exc())
            if not no_response_codes:
                self.response.set_status(exception.http_status, exception.human_message)
            self.data['status'] = exception.json_message
        elif isinstance(exception, ValueError):
            logging.info("ValueError:\n%s" % traceback.format_exc())
            if not no_response_codes:
                self.response.set_status(400, "Invalid parameter")
            self.data['status'] = 'ERROR_INVALID_PARAMETER'
        else:
            logging.error("Unhandled exception:\n%s" % traceback.format_exc())
            if not no_response_codes:
                self.response.set_status(500)

            report_error()

            self.data['status'] = 'ERROR_INTERNAL_FAILURE'
    
    @property
    def user(self):
        if not hasattr(self, 'current_user'):
            self.current_user = users.get_current_user()
        return self.current_user

