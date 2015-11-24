#!/usr/bin/env python

import time
import logging

from google.appengine.ext import ndb


def do_magic():
    example_model_instance = ExampleModel(name="Urban")
    example_model_instance.put()

    example_model_instance.log_name()

    return example_model_instance


class ExampleModel(ndb.Model):
    name = ndb.StringProperty()

    # timestamps
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    def log_name(self):
        logging.info("My name is %s", self.name)

    def serizlie(self):
        return {
            'key': str(self.key),
            'name': self.name,
            'created_at': time.mktime(self.created_at.timetuple()),
            'updated_at': time.mktime(self.updated_at.timetuple())
        }
