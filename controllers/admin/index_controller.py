#!/usr/bin/env python
# coding=utf8

import logging
import webapp2
import datetime

from controllers import application
from admin_users.admin_auth import requires_role


class IndexHandler(application.RequestHandler):
    @requires_role(role=3)
    def get(self):
        self.template = 'admin/index.html'
