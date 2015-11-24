#!/usr/bin/env python
# coding=utf8

from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from wtforms import Form, validators, fields
from .models import AdminUser, ROLES


class AdminUserBaseForm(Form):
    # Add form-fields not related to model.
    send_welcome_email = fields.BooleanField(label='Send welcome email')


# Use a app-engine plugin for making a form-class from a ndb-model.
AdminUserForm = model_form(AdminUser, base_class=AdminUserBaseForm, field_args={
    'role': {
        'choices': list(enumerate(ROLES)),  # Make a list of (index, value)
        'coerce': int
    }
})
