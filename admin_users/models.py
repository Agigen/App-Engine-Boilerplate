#!/usr/bin/env python
# coding=utf8

import logging

from google.appengine.ext import ndb

ROLES = ['super-admin', 'admin', 'viewer']
AU_KN = 'admin_user_%s'


class AdminUser(ndb.Model):
    email = ndb.StringProperty()
    role = ndb.IntegerProperty()
    google_user = ndb.UserProperty()

    @staticmethod
    def get_by_email(email):
        # TODO: Cache.
        u = AdminUser.query(AdminUser.email == email).fetch(1)
        if u:
            return u[0]
