#!/usr/bin/env python
#coding=utf8

import logging
import webapp2
import datetime

from controllers import application


class IndexHandler(application.RequestHandler):
    def head(self):
        pass
    def get(self):
        self.template = 'public/index.html'
