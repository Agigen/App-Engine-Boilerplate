#!/usr/bin/env python
#coding=utf8

import logging
import webapp2
import datetime

from controllers import application
import auth

class IndexHandler(application.RequestHandler):

    @auth.require_auth
    def get(self):
        self.template = 'public/index.html'
