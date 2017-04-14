# coding=utf-8
from collective.mustread import utils
from collective.mustread.interfaces import ITracker
from collective.mustread.testing import FunctionalBaseTestCase
from collective.mustread.tracker import Tracker
from plone import api
from plone.app.testing import logout
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.interface.verify import verifyObject

import datetime
import unittest


class TestTracker(FunctionalBaseTestCase):

    def test_interface(self):
        self.assertTrue(verifyObject(ITracker, Tracker()))

    def test_utility(self):
        tracker = getUtility(ITracker)
        self.assertTrue(verifyObject(ITracker, tracker))

    def test_mark_read(self):
        self.assertEqual(self.db.reads, [])
        self.tracker.mark_read(self.page)
        self.assertEqual(self.db.reads[-1].status, 'read')
        self.assertEqual(self.db.reads[-1].userid, TEST_USER_ID)

    def test_mark_read_userid(self):
        self.assertEqual(self.db.reads, [])
        self.tracker.mark_read(self.page, userid='foo')
        self.assertEqual(self.db.reads[-1].status, 'read')
        self.assertEqual(self.db.reads[-1].userid, 'foo')

    def test_mark_read_only_once(self):
        read_at = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        self.assertEqual(self.db.reads, [])
        self.tracker.mark_read(self.page, read_at=read_at)
        self.tracker.mark_read(self.page)
        self.assertEqual(1, len(self.db.reads))

    def test_mark_read_anon(self):
        logout()
        self.tracker.mark_read(self.page)
        self.assertEqual(self.db.reads, [])

    def test_has_read_anon(self):
        logout()
        self.tracker.mark_read(self.page)
        self.assertFalse(self.tracker.has_read(self.page))

    def test_has_read_noread(self):
        self.assertFalse(self.tracker.has_read(self.page))

    def test_has_read_read(self):
        self.tracker.mark_read(self.page)
        self.assertTrue(self.tracker.has_read(self.page))

    def test_has_read_userid(self):
        self.tracker.mark_read(self.page, userid='foo')
        self.assertTrue(self.tracker.has_read(self.page, userid='foo'))

    def test_uids_read_none(self):
        self.assertEqual([], self.tracker.uids_read())

    def test_uids_read_current(self):
        self.tracker.mark_read(self.page)
        self.assertEqual([utils.getUID(self.page)], self.tracker.uids_read())

    def test_uids_read_userid(self):
        self.tracker.mark_read(self.page, userid='foo')
        self.assertEqual([utils.getUID(self.page)],
                         self.tracker.uids_read('foo'))

    def test_has_read_userid_other(self):
        self.tracker.mark_read(self.page)
        self.assertFalse(self.tracker.has_read(self.page, userid='foo'))

    def test_who_read_unread(self):
        self.assertEqual([], self.tracker.who_read(self.page))

    def test_who_read(self):
        self.tracker.mark_read(self.page)
        self.assertEqual([TEST_USER_ID],
                         self.tracker.who_read(self.page))

    def test_who_read_other(self):
        self.tracker.mark_read(self.page, userid='foo')
        self.assertEqual(['foo'],
                         self.tracker.who_read(self.page))

    def test_who_read_multi(self):
        self.tracker.mark_read(self.page)
        self.tracker.mark_read(self.page, userid='foo')
        self.tracker.mark_read(self.page, userid='bar')
        self.assertEqual(set([TEST_USER_ID, 'foo', 'bar']),
                         set(self.tracker.who_read(self.page)))


class TestTrackerTrending(FunctionalBaseTestCase):

    def setUp(self):
        super(TestTrackerTrending, self).setUp()
        self.pages = [(i, api.content.create(type='Document',
                                             id='page%02d' % i,
                                             title='Page %02d' % i,
                                             container=self.portal))
                      for i in range(1, 10)]

    def test_most_read(self):
        for (i, page) in self.pages:
            for y in range(i):  # page01 1 read, page02 2 reads, etc
                self.tracker.mark_read(page, userid='user%02d' % (y + 1))
        result = [p for p in self.tracker.most_read()]
        expect = [x[1] for x in sorted(self.pages, reverse=True)]
        self.assertEqual(result, expect)

    def test_most_read_applies_status_filter(self):
        for (i, page) in self.pages:
            if not i % 2:  # only read even pages
                continue
            for y in range(i):
                self.tracker.mark_read(page, userid='user%02d' % (y + 1))
        result = [p for p in self.tracker.most_read()]
        expect = [x[1] for x in sorted(self.pages, reverse=True)
                  if x[0] % 2]
        self.assertEqual(result, expect)

    def test_most_read_limit(self):
        for (i, page) in self.pages:
            for y in range(i):  # page01 1 read, page02 2 reads, etc
                self.tracker.mark_read(page, userid='user%02d' % (y + 1))
        result = [p for p in self.tracker.most_read(limit=5)]
        expect = [x[1] for x in sorted(self.pages, reverse=True)][:5]
        self.assertEqual(result, expect)

    def test_most_read_dates(self):
        today = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        yesterday = today - datetime.timedelta(days=1)
        longago = today - datetime.timedelta(days=10)
        for (i, page) in self.pages:
            if i % 2:  # even
                read_at = yesterday
            else:  # odd
                read_at = longago
            for y in range(i):  # page01 1 read, page02 2 reads, etc
                self.tracker.mark_read(page, userid='user%02d' % (y + 1),
                                       read_at=read_at)
        result = [p for p in self.tracker.most_read(days=3)]
        expect = [x[1] for x in sorted(self.pages, reverse=True)
                  if x[0] % 2]
        self.assertEqual(result, expect)

    def test_most_read_dates_limit(self):
        today = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        yesterday = today - datetime.timedelta(days=1)
        longago = today - datetime.timedelta(days=10)
        for (i, page) in self.pages:
            if i % 2:  # even
                read_at = yesterday
            else:  # odd
                read_at = longago
            for y in range(i):  # page01 1 read, page02 2 reads, etc
                self.tracker.mark_read(page, userid='user%02d' % (y + 1),
                                       read_at=read_at)
        result = [p for p in self.tracker.most_read(days=3, limit=3)]
        expect = [x[1] for x in sorted(self.pages, reverse=True)
                  if x[0] % 2][:3]
        self.assertEqual(result, expect)

    def test_most_read_dates_verylongago(self):
        today = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        yesterday = today - datetime.timedelta(days=1)
        longago = today - datetime.timedelta(days=10)
        for (i, page) in self.pages:
            if i % 2:  # even
                read_at = yesterday
            else:  # odd
                read_at = longago
            for y in range(i):  # page01 1 read, page02 2 reads, etc
                self.tracker.mark_read(page, userid='user%02d' % (y + 1),
                                       read_at=read_at)
        result = [p for p in self.tracker.most_read(days=20)]
        expect = [x[1] for x in sorted(self.pages, reverse=True)]
        self.assertEqual(result, expect)

    def test_most_read_dates_verylongago_limit(self):
        today = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        yesterday = today - datetime.timedelta(days=1)
        longago = today - datetime.timedelta(days=10)
        for (i, page) in self.pages:
            if i % 2:  # even
                read_at = yesterday
            else:  # odd
                read_at = longago
            for y in range(i):  # page01 1 read, page02 2 reads, etc
                self.tracker.mark_read(page, userid='user%02d' % (y + 1),
                                       read_at=read_at)
        result = [p for p in self.tracker.most_read(days=20, limit=5)]
        expect = [x[1] for x in sorted(self.pages, reverse=True)][:5]
        self.assertEqual(result, expect)


class TestTrackerScheduled(FunctionalBaseTestCase):

    def setUp(self):
        super(TestTrackerScheduled, self).setUp()
        folder = api.content.create(self.portal, 'Folder', 'folder')
        self.page1 = api.content.create(folder, 'Document', title='Page 1')
        self.page2 = api.content.create(folder, 'Document', title='Page 2')
        self.page3 = api.content.create(folder, 'Document', title='Page 3')
        self.folder = folder
        self.deadline = datetime.datetime.utcnow() - datetime.timedelta(days=5)
        self.read_at = datetime.datetime.utcnow() - datetime.timedelta(days=3)

    def test_schedule_must_read(self):
        """schedule a must-read request and check if it has been
        written to the database"""
        users = self.tracker.schedule_must_read(self.page, ['user1'],
                                                self.deadline)
        self.assertEqual(users, ['user1'])
        self.assertEqual(len(self.db.reads), 1)
        entry = self.db.reads[0]
        self.assertEqual(entry.status, 'mustread')
        self.assertEqual(entry.uid, utils.getUID(self.page))
        self.assertEqual(entry.scheduled_by, None)
        self.assertEqual(entry.deadline, self.deadline)
        self.assertEqual(entry.scheduled_at.date(),
                         datetime.date.today())

        # optionally we can record who requested the review:
        users = self.tracker.schedule_must_read(self.page, ['user2'],
                                                self.deadline,
                                                'user1')
        entry = self.db.reads[-1]
        self.assertEqual(entry.scheduled_by, 'user1')

    def test_schedule_must_read_existing(self):
        """existing mustread request for an object do not get
        overwritten, we return ids of users a request has
        been written for
        """
        users = self.tracker.schedule_must_read(self.page, ['user1'],
                                                self.deadline)
        self.assertEqual(users, ['user1'])
        self.assertEqual(len(self.db.reads), 1)
        # re-run with one existing and one new user
        users = self.tracker.schedule_must_read(
            self.page, ['user1', 'user2'], self.deadline)
        # only new user is returned
        self.assertEqual(users, ['user2'])
        self.assertEqual(len(self.db.reads), 2)

    def test_mark_scheduled_as_read(self):
        self.tracker.schedule_must_read(self.page, ['user1'],
                                        self.deadline)
        self.assertEqual(len(self.db.reads), 1)
        self.tracker.mark_read(self.page, 'user1')
        self.assertEqual(len(self.db.reads), 1)
        entry = self.db.reads[0]
        self.assertEqual(entry.status, 'read')
        self.assertEqual(entry.read_at.date(), datetime.date.today())

    def test_who_must_read(self):
        custom_deadline = datetime.datetime(2017, 12, 31, 23, 00)
        self.tracker.schedule_must_read(self.page, ['user1', 'user2'],
                                        self.deadline)
        self.tracker.schedule_must_read(self.page, ['user3'],
                                        custom_deadline)

        self.tracker.schedule_must_read(self.page1, ['user2', 'user3'],
                                        self.deadline)

        who = self.tracker.who_must_read(self.page)
        self.assertEqual(sorted(who.keys()), ['user1', 'user2', 'user3'])
        self.assertEqual(who['user1'], self.deadline)
        self.assertEqual(who['user2'], self.deadline)
        self.assertEqual(who['user3'], custom_deadline)

        # after user1 read the page, he is not listed in who_must_read anymore
        self.tracker.mark_read(self.page, 'user1', self.read_at)
        who = self.tracker.who_must_read(self.page)
        self.assertEqual(sorted(who.keys()), ['user2', 'user3'])

        who = self.tracker.who_must_read(self.page1)
        self.assertEqual(sorted(who.keys()), ['user2', 'user3'])

        who = self.tracker.who_must_read(self.page2)
        self.assertEqual(who.keys(), [])

    def test_what_to_read(self):
        self.tracker.schedule_must_read(self.page, ['user1', 'user2'],
                                        self.deadline)

        self.tracker.schedule_must_read(self.page1, ['user2', 'user3'],
                                        self.deadline)

        self.tracker.schedule_must_read(self.page2, ['user2'],
                                        self.deadline)

        # mark open request as read
        self.tracker.mark_read(self.page2, 'user2')
        # mark as read w/o any pending request
        self.tracker.mark_read(self.page3, 'user2')

        # no context given, all pages are returned
        to_read = self.tracker.what_to_read()
        self.assertEqual(to_read, [self.page1, self.page])

        # only return objects within a folder
        to_read = self.tracker.what_to_read(context=self.folder)
        self.assertEqual(to_read, [self.page1])

        # limit to user
        to_read = self.tracker.what_to_read(userid='user1')
        self.assertEqual(to_read, [self.page])

        # user and context combined
        to_read = self.tracker.what_to_read(context=self.folder,
                                            userid='user1')
        self.assertEqual(to_read, [])
        to_read = self.tracker.what_to_read(context=self.folder,
                                            userid='user3')
        self.assertEqual(to_read, [self.page1])

    def test_get_report(self):
        # no entries - report empty
        report = list(self.tracker.get_report())
        self.assertEqual(len(report), 0)

        # one item marked as read
        self.tracker.mark_read(self.page, 'user1')
        report = list(self.tracker.get_report())
        self.assertEqual(len(report), 1)

        all_keys = ['status', 'read_at', 'uid', 'userid', 'deadline', 'path',
                    'scheduled_at', 'type', 'id', 'scheduled_by']
        # check if all keys are contained
        self.assertTrue(set(report[0].keys()).issuperset(set(all_keys)))
        # check some values
        self.assertDictContainsSubset(
            dict(userid='user1',
                 status='read'),
            report[0])

        # test context filter
        self.tracker.schedule_must_read(self.page1, ['user2'], self.deadline)
        report = list(self.tracker.get_report(context=self.folder))
        self.assertEqual(len(report), 1)
        self.assertDictContainsSubset(
            dict(userid='user2',
                 status='mustread',
                 deadline=self.deadline),
            report[0])

        # test recursive=False
        report = list(self.tracker.get_report(context=self.folder,
                                              include_children=False))
        self.assertEqual(len(report), 0)

        # test user filter
        report = list(self.tracker.get_report(userid='user2'))
        self.assertEqual(len(report), 1)
        self.assertDictContainsSubset(
            dict(userid='user2',
                 status='mustread',
                 deadline=self.deadline),
            report[0])

        # test context and user combined
        report = list(self.tracker.get_report(context=self.folder,
                                              userid='user1'))
        self.assertEqual(len(report), 0)
        report = list(self.tracker.get_report(context=self.folder,
                                              userid='user2'))
        self.assertEqual(len(report), 1)

        # test date filter
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        report = list(self.tracker.get_report(start_date=yesterday))
        self.assertEqual(len(report), 2)
        # get_report compares to the date and ignores the time
        today = datetime.datetime.now()
        report = list(self.tracker.get_report(start_date=today))
        self.assertEqual(len(report), 2)
        # we don't have items scheduled or marked as read past tomorrow
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        report = list(self.tracker.get_report(start_date=tomorrow))
        self.assertEqual(len(report), 0)

        # test date user and context combined
        report = list(self.tracker.get_report(context=self.folder,
                                              userid='user2',
                                              start_date=yesterday))
        self.assertEqual(len(report), 1)
        report = list(self.tracker.get_report(context=self.folder,
                                              userid='user2',
                                              start_date=tomorrow))
        self.assertEqual(len(report), 0)

    @unittest.skip('test needs to be implemented')
    def test_get_report_csv(self):
        pass
