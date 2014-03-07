#!/usr/bin/env python
#coding=utf8

import logging
from controllers import application
from webapp2_extras.routes import HandlerPrefixRoute, PathPrefixRoute
from webapp2_extras.routes import RedirectRoute as Route


class NotFoundHandler(application.RequestHandler):
    def get(self):
        self.response.set_status(404, "Not Found")
        self.template = '404.html'

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': application.config.secret_key('session'),
    'cookie_args': {
        'httponly': True,
        'secure': application.config.secure_cookie
    }
}

app = application.webapp2.WSGIApplication([
    # default
    HandlerPrefixRoute('controllers.default.', [
        HandlerPrefixRoute('index_controller.', [
            Route('/', 'IndexHandler', 'index', strict_slash=True),
        ]),

    ]),

    # api
    HandlerPrefixRoute('controllers.api.', [
        HandlerPrefixRoute('api_controller.', [
            Route('/api/test', handler='TestHandler'),
        ]),
    ]),

    # admin
    HandlerPrefixRoute('controllers.admin.', [
        HandlerPrefixRoute('index_controller.', [
            Route('/admin', handler='IndexHandler', name="admin-index", strict_slash=True),
            Route('/admin/sidebar', handler='SidebarHandler', name="admin-sidebar", strict_slash=True),
        ]),
    ]),

    (r'/.+', NotFoundHandler), # must be routed last
], config=config)
