#!/usr/bin/env python
# coding=utf8

import logging
from functools import wraps, partial
from config import exceptions
from google.appengine.api import users
from admin_users.models import AdminUser


def requires_role(role=3):
    def invalid_auth(request_handler):
        raise exceptions.PermissionDeniedError()

    # Yo dawg i heard u like functions
    def decorator(f):
        @wraps(f)
        def decorated_function(request_handler, *args, **kwargs):
            # Define a partial function that we can run and return on success.
            rf = partial(f, request_handler, *args, **kwargs)

            # Check if user is administrator.
            _is_admin = users.is_current_user_admin()
            if _is_admin:
                logging.debug('User is app administrator. Allowed.')
                return rf()

            # Check if user is added to admin users.
            user = users.get_current_user()
            if not user:
                logging.debug('No google user present. Denied.')
                return invalid_auth(request_handler)

            u = AdminUser.get_by_email(user.email())
            if not u:
                logging.debug('User not present in database. Denied.')
                return invalid_auth(request_handler)

            if u.role > role:
                logging.debug('User needs a higher permission level. Denied.')
                return invalid_auth(request_handler)

            return rf()
        return decorated_function

    return decorator
