# coding=utf-8
from plone.registry.interfaces import IRegistry

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.component import getUtility
from zope.globalrequest import getRequest

import logging
log = logging.getLogger(__name__)

DEBUG = False


def getEngine(conn_string=None, req=None):
    """
    cache this on the request object
    """
    if req is None:
        req = getRequest()
    if req and 'mustread.engine' in req.environ:
        engine = req.environ['mustread.engine']
    else:
        registry = getUtility(IRegistry)
        if conn_string is None:
            conn_string = registry['collective.mustread.interfaces.IMustReadSettings.connectionstring']  # noqa
        try:
            audit_conn_string = registry['collective.auditlog.interfaces.IAuditLogSettings.connectionstring']  # noqa
        except KeyError:
            audit_conn_string = None
        if conn_string == audit_conn_string \
           and req and 'sa.engine' in req.environ:
                # re-use collective.auditlog connector if possible
                engine = req.environ['sa.engine']
        else:
            engine = create_engine(conn_string, echo=DEBUG)
            if 'memory' in conn_string:
                log.warn(
                    'Running a in-memory database is NOT recommended '
                    'for production. Please check the registry setting '
                    'collective.mustread.interfaces.IMustReadSettings.')
        if req:
            req.environ['mustread.engine'] = engine
    return engine


def getSession(conn_string=None, engine=None, req=None):
    """
    same, cache on request object
    """
    if engine is None:
        engine = getEngine(conn_string)
    if req is None:
        req = getRequest()
    if req and 'mustread.session' in req.environ:
        session = req.environ['mustread.session']
    else:
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()
        if req:
            req.environ['mustread.session'] = session
    return session
