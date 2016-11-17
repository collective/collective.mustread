# coding=utf-8
from collective.mustread import db
from collective.mustread import td
from collective.mustread import utils
from collective.mustread.interfaces import ITracker
from collective.mustread.models import MustRead

from datetime import datetime
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implementer


@implementer(ITracker)
class Tracker(object):
    '''
    Database API. See ``interfaces.ITracker`` for API contract.
    '''

    def mark_read(self, obj, userid=None):
        '''Mark <obj> as read.'''
        data = dict(
            userid=self._resolve_userid(userid),
            read=datetime.utcnow(),
            status='read',
            uid=utils.getUID(obj),
            type=obj.portal_type,
            title=obj.Title(),
            path='/'.join(obj.getPhysicalPath()),
            site_name=utils.hostname(),
        )
        self._write(**data)

    def has_read(self, obj, userid=None):
        query_filter = dict(
            userid=self._resolve_userid(userid),
            status='read',
            uid=utils.getUID(obj),
        )
        result = self._read(**query_filter)
        return bool(result.all())

    def who_read(self, obj):
        raise NotImplementedError()

    def must_read(self, obj, userids=None, deadline=None):
        raise NotImplementedError()

    def who_unread(self, obj, force_deadline=True):
        raise NotImplementedError()

    def _resolve_userid(self, userid=None):
        if userid:
            return userid
        else:
            return api.user.get_current().id

    def _write(self, **data):
        session = self._get_session()
        data = self._safe_unicode(**data)
        record = MustRead(**data)
        session.add(record)

    def _read(self, **query_filter):
        session = self._get_session()
        query_filter = self._safe_unicode(**query_filter)
        return session.query(MustRead).filter_by(**query_filter)

    def _get_session(self):
        # make sure to join the transaction before we start
        session = db.getSession()
        tdata = td.get()
        if not tdata.registered:
            tdata.register(session)
        return session

    def _safe_unicode(self, **data):
        for key in data:
            value = data[key]
            if isinstance(value, str):
                data[key] = safe_unicode(value)
        return data
