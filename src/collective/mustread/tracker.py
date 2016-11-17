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


class InvalidParameterError(ValueError):
    pass


@implementer(ITracker)
class Tracker(object):
    '''
    Database API. See ``interfaces.ITracker`` for API contract.
    '''

    def mark_read(self, obj, userid=None, user=None):
        '''Mark <obj> as read.'''
        data = dict(
            userid=self._resolve_userid(userid, user),
            read=datetime.utcnow(),
            status='read',
            uid=utils.getUID(obj),
            type=obj.portal_type,
            title=obj.Title(),
            path='/'.join(obj.getPhysicalPath()),
            site_name=utils.hostname(),
        )
        self._write(**data)

    def has_read(self, obj, userid=None, user=None):
        raise NotImplementedError()

    def who_read(self, obj, deadline=None):
        raise NotImplementedError()

    def must_read(self, obj, userids=None, users=None, deadline=None):
        raise NotImplementedError()

    def who_unread(self, obj, force_deadline=True):
        raise NotImplementedError()

    def _resolve_userid(self, userid=None, user=None):
        if userid and user:
            raise InvalidParameterError(
                'You cannot specify both userid AND user')
        if userid:
            return userid
        elif user:
            return user.id
        else:
            return api.user.get_current().id

    def _write(self, **data):
        # make sure to join the transaction before we start
        session = db.getSession()
        tdata = td.get()
        if not tdata.registered:
            tdata.register(session)

        for key in data:
            value = data[key]
            if isinstance(value, str):
                data[key] = safe_unicode(value)

        record = MustRead(**data)
        session.add(record)
