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


class ITrackReadEnabledMarker(Interface):
    '''
    Marker interface for content objects that have the
    .behaviors.tracker.ITrackReadEnabled behavior.

    This is needed so we can bind the @@mustread-hit view
    to the marker interface. See:
    http://docs.plone.org/external/plone.app.dexterity/docs/behaviors/providing-marker-interfaces.html
    '''


class ITracker(Interface):
    '''
    Database API.
    Store which objects have been read by which users, and query that info.

    This API is designed to support two different use cases:

    1. Track reads on an object, without specifying beforehand which users
       should read that object, and query which users read the object:

    - mark_read(obj, 'maryjane')
    - has_read(obj, 'johndoe')
    - who_read(obj)

    This is the initial implementation. It is not required (and at this stage
    not even possible) to schedule a ``must_read(obj)`` to track reads.

    Scheduled for later extension:

    2. Specify which users should read an object, with a deadline; then
       track reads on that object, and query which users have failed to
       meet the requirment of reading the object in time:

    - must_read(obj, ['johndoe', 'maryjane'], nextweek)
    - mark_read(obj, 'johndoe')
    - who_unread(obj)

    The second scenario is a superset of the first. Specifically, also
    users who were not scheduled as ``must_read`` will be tracked and
    returned when you query ``who_read(obj)``.

    Note that we use userids not usernames, since userids will be more stable.
    This deviates from the records stored by collective.auditlog which use
    usernames.
    '''

    def mark_read(obj, userid=None, read_at=None):
        '''Mark an object as read by a user.

        If userid is None, defaults to currently logged-in user.

        If read_at is None, defaults to now.

        If the object was already marked read for this user,
        calling ``mark_read`` again will have no effect and avoids
        a database write.

        :param obj: Object to be marked as read
        :type obj: Content object (must be IUUID resolvable)
        :param userid: Userid of the user that viewed the object.
        :type userid: string
        :param read_at: Datetime at which the user read the object.
        :type read_at: datetime
        '''

    def has_read(obj, userid=None):
        '''Query whether an object was read by a user.

        If userid is None, defaults to currently logged-in user.

        :param obj: Object that should be read by user
        :type obj: Content object (must be IUUID resolvable)
        :param userid: Userid of the user that viewed the object.
        :type userid: string
        :returns: Whether the user has read this content object.
        :rtype: Bool
        '''

    def uids_read(userid=None):
        '''Query which objects have been read by a user.

        If userid is None, defaults to currently logged-in user.

        :param userid: Userid of the user that viewed the object.
        :type userid: string
        :returns: List of content uids (not objects)
        :rtype: List
        '''

    def who_read(obj):
        '''Query which users have read an object.

        :param obj: Object that should be read by users
        :type obj: Content object (must be IUUID resolvable)
        :returns: Userids of all users that read the object
        :rtype: List
        '''

    def most_read(days=None, limit=None):
        '''Query which content objects have been read most.

        Returns a sequence of content objects, sorted by the number of
        unique users who have read that object, in descending order
        of user count.

        Considers only the last <days> if given.
        Limits the result set to <limit> objects if given.

        :param days: Number of days before now to consider.
        :type days: int
        :param limit: Number of content objects to return
        :type limit: int
        :returns: Generator with content objects
        :rtype: Generator
        '''

    #  ------- @frisi --- TO BE IMPLEMENTED ---------------------------------

    def schedule_must_read(obj, userids, deadline=None):
        '''
        Schedule that an object must be read by some users before a deadline.

        Calling this method is optional. An object does not have to be
        scheduled as 'must-read' in order to track reads.

        Calling this method and scheduling an object as 'must-read' enables
        tracking of 'unread' status for specific sets of users and querying
        for those via the ``who_unread`` method.

        :param obj: Object that should be read by users
        :type obj: Content object (must be IUUID resolvable)
        :param userids: Userids of the users that should view the object.
        :type userid: List
        :param deadline: Deadline before which users should view the object.
        :type deadline: datetime
        '''

    def who_unread(obj, force_deadline=True):
        '''
        For an object scheduled as must-read, query which users have not
        read the object. Only makes sense of you first scheduled ``must_read``
        which is optional.

        This only queries for users who have been  explicitly scheduled via
        the ``must_read()`` method. If no users were scheduled, returns an
        empty list.

        If ``force_deadline`` is True, returns scheduled users who
        did not read the object before the deadline. This includes users
        who may have read the object *after* the deadline.

        If ``force_deadline`` is False, returns scheduled users who
        did not read the object at all.

        :param obj: Object that should be read by users
        :type obj: Content object (must be IUUID resolvable)
        :param force_deadline: Whether to ignore reads after the deadline
        :type force_deadline: Bool
        :returns: Userids of users scheduled for reading which did not read
        :rtype: List
        '''
