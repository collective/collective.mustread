# -*- coding: utf-8 -*-
from collective.mustread.behaviors.maybe import IMaybeMustRead
from collective.mustread.behaviors.track import ITrackReadEnabled
from collective.mustread.testing import FunctionalBaseTestCase
from plone.app.testing import TEST_USER_ID
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility
from zope.interface.verify import verifyObject


class TestMaybeMustRead(FunctionalBaseTestCase):

    def test_installed(self):
        name = 'collective.mustread.behaviors.maybe.IMaybeMustRead'
        behavior = getUtility(IBehavior, name=name)
        self.assertEqual(behavior.interface, IMaybeMustRead)
        self.assertTrue(IFormFieldProvider.providedBy(behavior.interface))

    def test_schema_default(self):
        adapted = IMaybeMustRead(self.page)
        self.assertFalse(adapted.must_read)

    def test_write_roundtrip(self):
        adapted = IMaybeMustRead(self.page)
        adapted.must_read = True
        adapted2 = IMaybeMustRead(self.page)
        self.assertTrue(adapted2.must_read)


class TestTrackReadEnabled(FunctionalBaseTestCase):

    def test_installed(self):
        name = 'collective.mustread.behaviors.track.ITrackReadEnabled'
        behavior = getUtility(IBehavior, name=name)
        self.assertEqual(behavior.interface, ITrackReadEnabled)

    def test_interface(self):
        adapted = ITrackReadEnabled(self.page)
        self.assertTrue(verifyObject(ITrackReadEnabled, adapted))

    def test_has_read_unread(self):
        adapted = ITrackReadEnabled(self.page)
        self.assertFalse(adapted.has_read())

    def test_mark_read_has_read(self):
        adapted = ITrackReadEnabled(self.page)
        adapted.mark_read()
        adapted2 = ITrackReadEnabled(self.page)
        self.assertTrue(adapted2.has_read())

    def test_who_read(self):
        adapted = ITrackReadEnabled(self.page)
        adapted.mark_read()
        adapted2 = ITrackReadEnabled(self.page)
        self.assertEqual([TEST_USER_ID], adapted2.who_read())
