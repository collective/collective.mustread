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
from sqlalchemy import or_
from zope.globalrequest import getRequest
from zope.interface import implementer

import csv
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
        userid = self._resolve_userid(userid)
        uid = utils.getUID(obj)

        open_request = self._read(userid=userid, uid=uid).all()
        if open_request:
            # mark existing entry as read and do not create a new entry
            open_request[0].status = 'read'
            open_request[0].read_at = read_at
            return

        data = dict(
            userid=userid,
            read_at=read_at,
            status='read',
            uid=uid,
            type=obj.portal_type,
            path='/'.join(obj.getPhysicalPath()),
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
                              func.count(MustRead.userid))
        if days:
            read_at = datetime.utcnow() - timedelta(days=days)
            query = query.filter(MustRead.read_at >= read_at)
        query = query.filter(MustRead.status == 'read')\
                     .group_by(MustRead.uid)\
                     .order_by(func.count(MustRead.userid).desc())\
                     .limit(limit)
        for record in self.query_all(query):
            yield api.content.get(UID=record.uid)

    def schedule_must_read(self, obj, userids, deadline, by=None):
        path = '/'.join(obj.getPhysicalPath())
        uid = utils.getUID(obj)
        now = datetime.utcnow()
        new_users = []

        # get existing read requests for this object (having a deadline)
        session = self._get_session()
        query = session.query(MustRead)
        query = query.filter(MustRead.deadline).filter(MustRead.uid == uid)
        existing_requests = [m.userid for m in query.all()]

        for userid in userids:
            if userid in existing_requests:
                # skip users that already have a mustread request
                log.info('user {0} already has a read request for {1}'.format(
                    userid, path))
                continue

            existing_read = self._read(
                userid=userid, uid=uid, status='read', deadline=None).all()
            if existing_read:
                # mark existing entry as mustread
                existing_read[0].status = 'mustread'
                existing_read[0].read_at = None
                existing_read[0].deadline = deadline
                existing_read[0].scheduled_at = now
                existing_read[0].scheduled_by = by
                new_users.append(userid)
                continue

            new_users.append(userid)
            data = dict(
                userid=userid,
                status=u'mustread',
                deadline=deadline,
                scheduled_at=now,
                uid=uid,
                type=obj.portal_type,
                path=path,
            )
            if by:
                data['scheduled_by'] = by
            self._write(**data)
        return new_users

    def what_to_read(self, context=None, userid=None, force_deadline=False,
                     deadline_before=None):
        session = self._get_session()
        query = session.query(MustRead.uid).group_by(MustRead.uid)

        if force_deadline:
            query = query.filter(or_(
                MustRead.deadline < MustRead.read_at,
                MustRead.status == 'mustread'))
        else:
            query = query.filter(MustRead.status == 'mustread')

        path = '/'.join(api.portal.get().getPhysicalPath())
        if context is not None:
            path = '/'.join(context.getPhysicalPath())
        query = query.filter(MustRead.path.startswith(path))

        if userid is not None:
            query = query.filter(MustRead.userid == unicode(userid))
        if deadline_before:
            query = query.filter(MustRead.deadline < deadline_before)
        query = query.order_by(MustRead.path)
        uids = [r[0] for r in self.query_all(query)]
        result = []
        for uid in uids:
            obj = api.content.get(UID=uid)
            if obj is None:
                log.warning('mustread db contains broken uid: ' + uid)
                continue
            result.append(obj)
        return result

    def who_did_not_read(self, obj, force_deadline=False,
                         deadline_before=None):
        session = self._get_session()
        query = session.query(MustRead)
        query = query.filter(MustRead.uid == utils.getUID(obj))
        if force_deadline:
            query = query.filter(or_(
                MustRead.deadline < MustRead.read_at,
                MustRead.status == 'mustread'))
        else:
            query = query.filter(MustRead.status == 'mustread')

        if deadline_before:
            query = query.filter(MustRead.deadline < deadline_before)

        return dict([(m.userid, m.deadline) for m in query.all()])

    def get_report(self, context=None, include_children=True, userid=None,
                   start_date=None):
        path = '/'.join(api.portal.get().getPhysicalPath())
        if context is not None:
            path = '/'.join(context.getPhysicalPath())

        session = self._get_session()
        query = session.query(MustRead)

        if start_date:
            query = query.filter(or_(
                MustRead.scheduled_at >= start_date.date(),
                MustRead.read_at >= start_date.date()))

        if userid:
            query = query.filter(MustRead.userid == unicode(userid))
        if include_children:
            query = query.filter(MustRead.path.startswith(path))
        else:
            query = query.filter(MustRead.path == path)

        query = query.order_by(MustRead.path)

        for item in query.all():
            # remove sqlalchemy specific data
            # (see discussion at http://stackoverflow.com/q/1958219/810427)
            yield dict([(k, v) for k, v in item.__dict__.iteritems()
                        if not k.startswith('_')])

    def get_report_csv(self, csvfile, context=None, include_children=True,
                       fieldnames=[]):
        if not fieldnames:
            fieldnames = [
                'path', 'userid', 'read_at', 'deadline', 'scheduled_at',
                'scheduled_by', 'status', 'uid', 'type']

        writer = csv.DictWriter(csvfile, fieldnames, extrasaction='ignore')
        writer.writeheader()
        for item in self.get_report(context, include_children):
            writer.writerow(item)

    def unschedule_must_read(self, obj=None, userids=None):
        # maintenance methods need to be implemented
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
