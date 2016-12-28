# coding=utf-8
from collective.mustread import db
from collective.mustread import td
from collective.mustread import utils
from collective.mustread.interfaces import ITracker
from collective.mustread.models import MustRead

from datetime import datetime
from datetime import timedelta
from plone import api
from Products.CMFPlone.utils import safe_unicode
from sqlalchemy import func
from zope.globalrequest import getRequest
from zope.interface import implementer

import logging
log = logging.getLogger(__name__)


@implementer(ITracker)
class Tracker(object):
    '''
    Database API. See ``interfaces.ITracker`` for API contract.
    '''

    def mark_read(self, obj, userid=None, read_at=None):
        '''Mark <obj> as read.'''
        # block anon
        if not userid and api.user.is_anonymous():
            return
        # avoid database writes by only storing first read actions
        if self.has_read(obj, userid):
            return
        if not read_at:
            read_at = datetime.utcnow()
        data = dict(
            userid=self._resolve_userid(userid),
            read_at=read_at,
            status='read',
            uid=utils.getUID(obj),
            type=obj.portal_type,
            title=obj.Title(),
            path='/'.join(obj.getPhysicalPath()),
            site_name=utils.hostname(),
        )
        self._write(**data)

    def has_read(self, obj, userid=None):
        # block anon
        if not userid and api.user.is_anonymous():
            return False
        query_filter = dict(
            userid=self._resolve_userid(userid),
            status='read',
            uid=utils.getUID(obj),
        )
        result = self._read(**query_filter)
        return bool(result.all())

    def uids_read(self, userid=None):
        # block anon
        if not userid and api.user.is_anonymous():
            return False
        query_filter = dict(
            userid=self._resolve_userid(userid),
            status='read',
        )
        query = self._read(**query_filter)
        return [x.uid for x in self.query_all(query)]

    def who_read(self, obj):
        query_filter = dict(
            status='read',
            uid=utils.getUID(obj),
        )
        query = self._read(**query_filter)
        return [x.userid for x in self.query_all(query)]

    def most_read(self, days=None, limit=None):
        session = self._get_session()
        query = session.query(MustRead.uid,
                              func.count(MustRead.userid),
                              MustRead.title)
        if days:
            read_at = datetime.utcnow() - timedelta(days=days)
            query = query.filter(MustRead.read_at >= read_at)
        query = query.filter(MustRead.status == 'read')\
                     .group_by(MustRead.uid)\
                     .order_by(func.count(MustRead.userid).desc())\
                     .limit(limit)
        for record in self.query_all(query):
            yield api.content.get(UID=record.uid)

    def schedule_must_read(self, obj, userids=None, deadline=None):
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

    def query_all(self, query):
        """Wrap query.all() in a try/except with Engine logging"""
        try:
            for record in query.all():
                yield record
        except Exception, exc:
            req = getRequest()
            log.error('Query error on %s', req.environ['mustread.engine'])
            raise exc

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
