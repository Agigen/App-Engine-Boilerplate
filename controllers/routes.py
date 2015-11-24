#!/usr/bin/env python
# coding=utf8

import logging
import sys

from controllers import application
from webapp2_extras.routes import HandlerPrefixRoute, PathPrefixRoute
from webapp2_extras.routes import RedirectRoute as Route

import simple_auth
import config.application


class NotFoundHandler(application.RequestHandler):
    def get(self):
        self.response.set_status(404, "Not Found")
        self.template = '404.html'

webapp_config = {}
webapp_config['webapp2_extras.sessions'] = {
    'secret_key': config.application.secret_key('session'),
    'cookie_args': {
        'httponly': True,
        'secure': config.application.secure_cookie
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
        HandlerPrefixRoute('admin_user_controller.', [
            Route('/admin/admin-users', handler='AdminUsersHandler', name="admin-users-all", strict_slash=True),
            Route('/admin/admin-users/<user_id>', handler='AdminUserHandler', name="admin-user", strict_slash=True),
        ]),
    ]),

    (r'/login', simple_auth.LoginHandler),
    (r'/.+', NotFoundHandler), # must be routed last
], config=webapp_config)
