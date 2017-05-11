# coding=utf-8
from collective.mustread.db import getSession
from collective.mustread.interfaces import IMustReadSettings
from collective.mustread.models import Base
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zope import interface

import logging
import os


logger = logging.getLogger('collective.mustread')


class InitView(BrowserView):
    ''' Initialize the DB

    If memory db is configured, replace it with a
    sqlite mustread.db file in buildout/var directory

    if another path/db is given in the record, make sure
    the necessary tables for your model get created.
    '''

    def __call__(self):
        if api.env.test_mode() or 'robot-server' in os.environ.get('_', ''):
            # tests provide own tempDb
            return 'running tests - no database created'
        interface.alsoProvides(self.request, IDisableCSRFProtection)
        try:
            record = api.portal.get_registry_record(
                'connectionstring', interface=IMustReadSettings)
        except api.exc.InvalidParameterError:
            record = ''
        if not record or 'memory' in record:
            dbpath = '%s/var/mustread.db' % os.getcwd()
            record = u'sqlite:///%s' % dbpath
            logger.warn(
                'SQL storage not properly configured. Forcing: %s', record)
            api.portal.set_registry_record(
                'connectionstring', record, interface=IMustReadSettings)
        logger.info('Initializing SQL db: %s' % record)
        session = getSession()
        Base.metadata.create_all(session.bind.engine)
        return 'configured db: ' + record
