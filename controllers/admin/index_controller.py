#!/usr/bin/env python
#coding=utf8

import logging
import webapp2
import datetime

from controllers import application


class IndexHandler(application.RequestHandler):
    def get(self):
        self.template = 'admin/index.html'

class SidebarHandler(application.RequestHandler):
    def get(self):
        self.template = 'admin/sidebar.html'


class NotFoundHandler(application.RequestHandler):
    def get(self):
        self.response.set_status(404, "Not Found")
        self.template = '404.html'




app = application.webapp2.WSGIApplication([
    ('/admin/?', IndexHandler),
    ('/admin/sidebar/?', SidebarHandler),
    ('/admin/.+', NotFoundHandler), # must be routed last
])
