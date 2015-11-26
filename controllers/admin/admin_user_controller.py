#!/usr/bin/env python
#coding=utf8

import logging
import webapp2
import datetime

from controllers import application
from admin_users.models import ROLES, AU_KN, AdminUser
from admin_users.admin_auth import requires_role
from admin_users.forms import AdminUserForm
from google.appengine.api import mail
from config import exceptions

import config


class AdminUsersHandler(application.RequestHandler):
    @requires_role(role=3)
    def get(self):
        admin_users = AdminUser.query().fetch()
        self.data.update(admin_users=admin_users, ROLES=ROLES)

        self.template = 'admin/admin-users.html'


class AdminUserHandler(application.RequestHandler):
    _template = 'admin/admin-user-edit.html'

    @requires_role(role=3)
    def get(self, user_id):
        self.data.update(form=AdminUserForm())
        if user_id != 'add':
            admin_user = AdminUser.get_by_id(int(user_id))
            self.data.update(form=AdminUserForm(obj=admin_user), admin_user=admin_user)

        self.template = self._template

    @requires_role(role=0)
    def post(self, user_id):
        if user_id and user_id != 'add':
            u = AdminUser.get_by_id(int(user_id))
        else:
            # New user.
            u = AdminUser()

        form = AdminUserForm(self.request.POST)

        if form.validate():
            # Populate the user object with data from the form.
            form.populate_obj(u)
            u.put()

            if form.send_welcome_email.data:
                self.send_welcome_email(u.email)

            logging.debug('Updated admin user.')
            self.redirect(webapp2.uri_for('admin-users-all'))
        else:
            logging.debug('Errors in form')
            self.data.update(form=form)
            self.template = self._template


    def send_welcome_email(self, email_address):
        app_id = config.application.app_identity.get_application_id()
        mail.send_mail(
            sender="No-reply <robot@%s.appspotmail.com>" % (app_id),
            to=email_address,
            subject="Added as admin user for app %s" % (app_id),
            body="You were added as admin user for the application %s. Log in at %s. \nYou were added by %s" %
            (app_id, config.application.base_url + webapp2.uri_for('admin-index'), self.user.email())
        )


class AdminUserDeleteHandler(application.RequestHandler):
    def get(self, user_id):
        try:
            admin_user = AdminUser.get_by_id(int(user_id))
            assert admin_user
        except:
            raise exceptions.NoSuchEntityError()

        self.data.update(u=admin_user)
        self.template = 'admin/admin-user-delete.html'

    @requires_role(role=0)
    def post(self, user_id):
        u = AdminUser.get_by_id(int(user_id))
        u.key.delete()
        self.redirect(webapp2.uri_for('admin-users-all'))
