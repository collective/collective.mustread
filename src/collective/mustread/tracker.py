# coding=utf-8
from collective.mustread import db
from collective.mustread import td
from collective.mustread.models import LogEntry
from collective.mustread.utils import getUID
from datetime import datetime
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zope.globalrequest import getRequest


class Tracker(object):

    def getHostname(self, request):
        '''
        stolen from the developer manual
        '''

        if 'HTTP_X_FORWARDED_HOST' in request.environ:
            # Virtual host
            host = request.environ['HTTP_X_FORWARDED_HOST']
        elif 'HTTP_HOST' in request.environ:
            # Direct client request
            host = request.environ['HTTP_HOST']
        else:
            return None

        # separate to domain name and port sections
        host = host.split(':')[0].lower()

        return host

    def hit(self, obj):
        action = 'read'
        req = getRequest()
        data = dict(
            performed_on=datetime.utcnow(),
            info='',
            action=action,
            user=api.user.get_current().getUserName(),
            site_name=self.getHostname(req),
            uid=getUID(obj),
            type=obj.portal_type,
            title=obj.Title(),
            path='/'.join(obj.getPhysicalPath())
        )
        runJob(api.portal.get(), **data)


def runJob(context, **data):
    # make sure to join the transaction before we start
    session = db.getSession()
    tdata = td.get()
    if not tdata.registered:
        tdata.register(session)

    for key in data:
        value = data[key]
        if isinstance(value, str):
            data[key] = safe_unicode(value)

    log = LogEntry(**data)
    session.add(log)
