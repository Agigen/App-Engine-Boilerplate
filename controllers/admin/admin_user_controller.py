#!/usr/bin/env python
#coding=utf8

import logging
import webapp2
import datetime

from controllers import application
from admin_users.models import ROLES, AU_KN, AdminUser
from admin_users.admin_auth import requires_role

from google.appengine.api import mail

import config


class AdminUsersHandler(application.RequestHandler):
    @requires_role(role=3)
    def get(self):
        admin_users = AdminUser.query().fetch()
        self.data.update(admin_users=admin_users, ROLES=ROLES)
        self.template = 'admin/admin-users.html'


class AdminUserHandler(application.RequestHandler):
    @requires_role(role=3)
    def get(self, user_id):
        self.data.update(roles=ROLES, user_id=user_id)
        if user_id != 'add':
            admin_user = AdminUser.get_by_id(int(user_id))
            self.data.update(admin_user=admin_user)

        self.template = 'admin/admin-user-edit.html'

    @requires_role(role=0)
    def post(self, user_id):
        if user_id and user_id != 'add':
            u = AdminUser.get_by_id(int(user_id))
        else:
            # Check if user exists. If so, use that entity.
            u = AdminUser.get_by_email(self.request.get('email'))
            if not u:
                u = AdminUser()

        u.email = self.request.get('email')
        u.role = int(self.request.get('role', '3'))
        u.put()
        if self.request.get('send-email'):
            self.send_welcome_email(u.email)

        logging.debug('Updated admin user.')

        self.redirect(webapp2.uri_for('admin-users-all'))

    def send_welcome_email(self, email_address):
        app_id = config.application.app_identity.get_application_id()
        mail.send_mail(
            sender="No-reply <robot@%s.appspotmail.com>" % (app_id),
            to=email_address,
            subject="Added as admin user for app %s" % (app_id),
            body="You were added as admin user for the application %s. Log in at %s. \nYou were added by %s" %
            (app_id, config.application.base_url + webapp2.uri_for('admin-index'), self.user.email())
        )
