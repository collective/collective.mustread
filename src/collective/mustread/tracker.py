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

    def schedule_must_read(self, obj, userids, deadline):
        # get existing must read items for this object
        qry = self._read(uid=utils.getUID(obj))
        existing_users = [m.userid for m in qry.all()]

        path = '/'.join(obj.getPhysicalPath())
        uid = utils.getUID(obj)
        hostname = utils.hostname()
        now = datetime.utcnow()
        current_user = api.user.get_current().id
        new_users = []
        for userid in userids:
            if userid in existing_users:
                # skip uses that already read the item
                # or have an open mustread request
                log.info('user {0} already has read / has to read {1}'.format(
                    userid, path))
                continue
            # @guido: should we change the deadline for existing must_reads?
            new_users.append(userid)
            data = dict(
                userid=userid,
                status=u'mustread',
                deadline=deadline,
                scheduled_at=now,
                scheduled_by=current_user,
                uid=uid,
                type=obj.portal_type,
                title=obj.Title(),
                path=path,
                site_name=hostname,
            )
            self._write(**data)
        return new_users

    def what_to_read(self, context=None, userid=None):
        session = self._get_session()
        query = session.query(MustRead.uid).filter(
            MustRead.status != 'read').group_by(MustRead.uid)

        if context is not None:
            path = '/'.join(context.getPhysicalPath())
            query = query.filter(MustRead.path.startswith(path))
        if userid is not None:
            query = query.filter(MustRead.userid == unicode(userid))
        query = query.order_by(MustRead.path)
        uids = [r[0] for r in self.query_all(query)]
        for uid in uids:
            obj = api.content.get(UID=uid)
            if obj is None:
                log.warning('mustread db contains broken uid: ' + uid)
                continue
            yield obj

    def who_must_read(self, obj):
        must_reads = self._read(uid=utils.getUID(obj), status='mustread').all()
        return dict([(m.userid, m.deadline) for m in must_reads])

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
            query = query.filter(MustRead.userid == userid)
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

    def get_stats_csv(self, csvfile, context=None, recursive=True):
        """export mustread database entries for all objects within context
        csvfile is a file-like object with a write method
        (see csv.writer documentation)
        xxx if guido does not like csv creation here in the api we can move
        this to our contentrule
        [{userid, uid, status, read_at, deadline, scheduled_at, type, path,}]
        """

        fieldnames = ['path', 'userid', 'read_at', 'deadline', 'scheduled_at',
                      'scheduled_by', 'status', 'uid', 'type']

        writer = csv.DictWriter(csvfile, fieldnames, extrasaction='ignore')
        writer.writeheader()
        for item in self.get_stats(context, recursive):
            writer.writerow(item)

    def unschedule_must_read(self, obj=None, userids=None):
        # maintenance methods need to be implemented
        raise NotImplemented()

    def accept_not_read(self, obj=None, userids=None):
        # maintenance methods need to be implemented
        raise NotImplemented()

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
