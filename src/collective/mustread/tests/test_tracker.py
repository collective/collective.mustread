# coding=utf-8
from collective.mustread.db import getSession
from collective.mustread.interfaces import IMustReadSettings
from collective.mustread.models import Base
from collective.mustread.models import MustRead
from collective.mustread.testing import COLLECTIVE_MUSTREAD_FUNCTIONAL_TESTING
from collective.mustread.tracker import Tracker
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from tempfile import mkstemp
from zope.component import getUtility

import os
import unittest


class tempDb(object):

    registry_key = '{iface}.connectionstring'.format(
        iface=IMustReadSettings.__identifier__
    )
    session = None

    def __init__(self):
        _, self.tempfilename = mkstemp()

    @property
    def reads(self):
        return self.session.query(MustRead).all()

    def __enter__(self):
        self.registry = registry = getUtility(IRegistry)
        registry[self.registry_key] = (
            u'sqlite:///%s?check_same_thread=true' % (self.tempfilename)
        )
        self.session = getSession()
        Base.metadata.create_all(self.session.bind.engine)
        return self

    def __exit__(self, type, value, traceback):
        os.remove(self.tempfilename)


class TestTrack(unittest.TestCase):

    layer = COLLECTIVE_MUSTREAD_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request'].clone()
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def create_and_read_page(self, title='Page'):
        ''' Create a page and return it
        '''
        obj = api.content.create(type='Document',
                                 id='page',
                                 title=title,
                                 container=self.portal)

        tracker = Tracker()
        tracker.mark_read(obj)

        return obj

    def test_mark_read(self):
        with tempDb() as db:
            self.assertEqual(db.reads, [])
            self.create_and_read_page()
            self.assertEqual(db.reads[-1].action, 'read')
