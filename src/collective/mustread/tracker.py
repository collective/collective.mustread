# coding=utf-8
from collective.mustread import db
from collective.mustread import td
from collective.mustread import utils
from collective.mustread.models import MustRead

from datetime import datetime
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zope.globalrequest import getRequest


class Tracker(object):

    def mark_read(self, obj):
        '''Mark <obj> as read.'''
        action = 'read'
        req = getRequest()
        data = dict(
            performed_on=datetime.utcnow(),
            info='',
            action=action,
            user=api.user.get_current().getUserName(),
            site_name=utils.hostname(req),
            uid=utils.getUID(obj),
            type=obj.portal_type,
            title=obj.Title(),
            path='/'.join(obj.getPhysicalPath())
        )
        self._record(**data)

    def _record(self, **data):
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
