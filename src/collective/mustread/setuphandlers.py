# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from collective.mustread.db import getSession
from collective.mustread.interfaces import IMustReadSettings
from collective.mustread.models import Base
from plone import api
from zope.interface import implementer

import logging
import os


logger = logging.getLogger('collective.mustread')


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'collective.mustread:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def initialize_mustread_db(*args):
    """create a sqlite database in the buildout's var directory
    and create the necessary table definitions
    """

    if api.env.test_mode() or 'robot-server' in os.environ.get('_', ''):
        # tests provide own tempDb
        return
    try:
        record = api.portal.get_registry_record(
            'connectionstring', interface=IMustReadSettings)
    except api.exc.InvalidParameterError:
        record = ''
    if not record or 'memory' in record:
        dbpath = '%s/var/mustread.db' % os.getcwd()
        record = u'sqlite:///%s' % dbpath
        logger.warn('SQL storage not properly configured. Forcing: %s', record)
        api.portal.set_registry_record(
            'connectionstring', record, interface=IMustReadSettings)
    logger.info('Initializing SQL db: %s' % record)
    session = getSession()
    Base.metadata.create_all(session.bind.engine)
