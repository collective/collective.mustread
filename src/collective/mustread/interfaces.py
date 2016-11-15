# -*- coding: utf-8 -*-
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


_ = MessageFactory('collective.mustread')


class ICollectiveMustreadLayer(IDefaultBrowserLayer):
    '''Marker interface that defines a browser layer.'''


class IMustReadSettings(Interface):
    '''Must Read settings.
    This allows you to set the database connection string.
    '''

    connectionstring = schema.TextLine(
        title=_(u'Must Read Connection String'),
        description=_(
            u'help_mustread_connection',
            default=(
                u'Enter the connection string for the database Must Read '
                u'is to write to. '
                u'Must be a valid SQLAlchemy connection string. '
                u'This may be the same as a collective.auditlog connector. '
                u'MustRead will use a different database table and can  '
                u'coexist within the same database as collective.auditlog.'
            )
        ),
        required=True,
        default=u'sqlite:///:memory:',
    )
