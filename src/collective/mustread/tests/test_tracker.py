# coding=utf-8
from collective.mustread.db import getSession
from collective.mustread.interfaces import IMustReadSettings
from collective.mustread.interfaces import ITracker
from collective.mustread.models import Base
from collective.mustread.models import MustRead
from collective.mustread.testing import COLLECTIVE_MUSTREAD_FUNCTIONAL_TESTING
from collective.mustread.tracker import InvalidParameterError
from collective.mustread.tracker import Tracker
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from tempfile import mkstemp
from zope.component import getUtility
from zope.interface.verify import verifyObject

import os
import unittest


class tempDb(object):

    registry_key = '{iface}.connectionstring'.format(
        iface=IMustReadSettings.__identifier__
    )
    session = None

    def __init__(self):
        _, self.tempfilename = mkstemp()
        self.registry = registry = getUtility(IRegistry)
        registry[self.registry_key] = (
            u'sqlite:///%s?check_same_thread=true' % (self.tempfilename)
        )
        self.session = getSession()
        Base.metadata.create_all(self.session.bind.engine)

    def __del__(self):
        try:
            os.remove(self.tempfilename)
        except OSError:
            # __del__ is called more than once...
            pass

    @property
    def reads(self):
        return self.session.query(MustRead).all()


class TestTrack(unittest.TestCase):

    layer = COLLECTIVE_MUSTREAD_FUNCTIONAL_TESTING

    def setUp(self):
        self.db = tempDb()  # auto teardown via __del__
        self.portal = self.layer['portal']
        self.request = self.layer['request'].clone()
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.page = api.content.create(type='Document',
                                       id='page',
                                       title='Page',
                                       container=self.portal)
        self.tracker = Tracker()

    def test_interface(self):
        self.assertTrue(verifyObject(ITracker, Tracker()))

    def test_mark_read(self):
        self.assertEqual(self.db.reads, [])
        self.tracker.mark_read(self.page)
        self.assertEqual(self.db.reads[-1].status, 'read')
        self.assertEqual(self.db.reads[-1].userid, TEST_USER_ID)

    def test_mark_read_params(self):
        with self.assertRaises(InvalidParameterError):
            self.tracker.mark_read(self.page, userid='foo', user='bar')

    def test_mark_read_userid(self):
        self.assertEqual(self.db.reads, [])
        self.tracker.mark_read(self.page, userid='foo')
        self.assertEqual(self.db.reads[-1].status, 'read')
        self.assertEqual(self.db.reads[-1].userid, 'foo')

    def test_mark_read_user(self):
        self.assertEqual(self.db.reads, [])
        user = api.user.get_current()
        self.tracker.mark_read(self.page, user=user)
        self.assertEqual(self.db.reads[-1].status, 'read')
        self.assertEqual(self.db.reads[-1].userid, TEST_USER_ID)
