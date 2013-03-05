#!/usr/bin/env python
#coding=utf8

import logging
import webapp2
import datetime

from controllers import application



class TestHandler(application.APIRequestHandler):
    def get(self):
        self.data['testing'] = u"Hello world"




app = application.webapp2.WSGIApplication([
    ('/api/test', TestHandler),
])
