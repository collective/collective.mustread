# -*- coding: utf-8 -*-
from plone.uuid.interfaces import IUUID
from zope.globalrequest import getRequest


def getUID(context):
    uid = IUUID(context, None)  # noqa
    if uid is not None:
        return uid

    if hasattr(context, 'UID'):
        return context.UID()

    try:
        return '/'.join(context.getPhysicalPath())
    except AttributeError:
        pass

    try:
        return context.id
    except AttributeError:
        return ''


def hostname(request=None):
    '''
    stolen from the developer manual
    '''
    if not request:
        request = getRequest()

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
