#!/usr/bin/env python

import webapp2
import jinja2
import os
import json
import traceback
import logging
import datetime
from google.appengine.api import mail

from google.appengine.api import users

import includes.exceptions
import includes.config


class RequestHandler(webapp2.RequestHandler):
    require_roles = []
    def initialize(self, request, response):
        request.charset = 'utf-8'
        super(RequestHandler, self).initialize(request, response)
        self.data = {}
        self.data['config'] = includes.config
        self.data['request_path'] = request.path
        self.data['user'] = self.user
        
        self.template = None
        self.jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '..', 'templates')))

    def dispatch(self):
        return_value = super(RequestHandler, self).dispatch()
    
        if self.template:
            template = self.jinja_environment.get_template(self.template)
            self.response.out.write(template.render(self.data))
    
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
        else:
            logging.warning("Unhandled exception: %s" % traceback.format_exc())
            self.response.set_status(500, "Internal Server Error")

            try:
                mail.send_mail(
                    sender="Agigen Appengine App <error@%s.appspotmail.com>" % includes.config.app_identity.get_application_id(),
                    to="Agigen Appengine Error <appengine_error@agigen.se>",
                    subject="%s: %s has encountered an unhandeled exception" % (str(datetime.datetime.now()), includes.config.app_identity.get_application_id()),
                    body="Unhandled exception: %s" % traceback.format_exc())
            except Exception, e:
                logging.error('Could not send email about error: %s' % str(e))

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

            try:
                mail.send_mail(
                    sender="Agigen Appengine App <error@%s.appspotmail.com>" % includes.config.app_identity.get_application_id(),
                    to="Agigen Appengine Error <appengine_error@agigen.se>",
                    subject="%s: %s has encountered an unhandeled exception" % (str(datetime.datetime.now()), includes.config.app_identity.get_application_id()),
                    body="Unhandled exception: %s" % traceback.format_exc())
            except Exception, e:
                logging.error('Could not send email about error')

            self.data['status'] = 'ERROR_INTERNAL_FAILURE'
    
    @property
    def user(self):
        if not hasattr(self, 'current_user'):
            self.current_user = users.get_current_user()
        return self.current_user

