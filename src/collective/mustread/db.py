# coding=utf-8
from plone.registry.interfaces import IRegistry
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.component import getUtility
from zope.globalrequest import getRequest


def getEngine(conn_string=None, req=None):
    """
    cache this on the request object
    """
    if req is None:
        req = getRequest()
    if req and 'mustread.engine' in req.environ:
        engine = req.environ['mustread.engine']
    else:
        if conn_string is None:
            registry = getUtility(IRegistry)
            conn_string = registry['collective.mustread.interfaces.IMustReadSettings.connectionstring']  # noqa
        engine = create_engine(conn_string)
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
