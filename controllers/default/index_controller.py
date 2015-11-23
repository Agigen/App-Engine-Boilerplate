#!/usr/bin/env python
#coding=utf8

import logging
import webapp2
import datetime

from controllers import application
import simple_auth

class IndexHandler(application.RequestHandler):

    @simple_auth.require_auth
    def get(self):
        self.template = 'public/index.html'
