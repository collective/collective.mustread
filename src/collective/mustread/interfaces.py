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

    connectionparameters = schema.TextLine(
        title=_(u'Must Read Connection Parameters'),
        description=_(
            u'help_mustread_connection_parameteers',
            default=(
                u'Enter the connection parametes in a json form. '
                u'E.g.: `{"pool_recycle": 3600, "echo": true}` '
            )
        ),
        required=True,
        default=u'',
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
    - uids_read('johndoe')
    - most_read(10, 5)  # top 5 objects in the last 10 days

    2. Specify which users should read an object, with a deadline; then
       track reads on that object, and query which users have failed to
       meet the requirment of reading the object in time:

    - schedule_must_read(obj, ['johndoe', 'maryjane'], nextweek)
    - unschedule_must_read(obj, ['johndoe'])
    - mark_read(obj, 'johndoe')
    - who_did_not_read(obj) #
    - who_did_not_read(obj, force_deadline=True, deadline_before=today_0_am)
      (all users that missed their deadlines)
    - what_to_read(context)
    - what_to_read(userid)

    The second scenario is a superset of the first. Specifically, also
    users who were not scheduled as ``schedule_must_read`` will be tracked and
    returned when you query ``who_read(obj)``.

    In addition we provide methods to obtain reports for objects/users

    - get_report(folder, 'john', recursive, read_or_sheduled_after_lastweek)
    - get_report_csv(csvfile, folder, recursive, ['path', 'userid', 'status'])

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

    def schedule_must_read(obj, userids, deadline, by=None):
        '''Schedule that an object must be read by some users before a deadline.

        Calling this method is optional. An object does not have to be
        scheduled as 'must-read' in order to track reads.

        Calling this method and scheduling an object as 'must-read' enables
        tracking of 'unread' status for specific sets of users and querying
        for those via the ``who_did_not_read`` method.

        If the object has been scheduled as must_read for a user before, do not
        update the existing record (use unschedule_must_read to remove the read
        request before).
        If the object has been marked as read for a user before without an
        existing read request, remove the 'read' status and schedule a request

        :param obj: Object that should be read by users
        :type obj: Content object (must be IUUID resolvable)
        :param userids: Userids of the users that should view the object.
        :type userids: List
        :param deadline: Deadline before which users should view the object.
        :type deadline: datetime
        :param by: Userid that scheduled the must read request
        :type by: string
        :returns: List of userids a mustread deadline has been scheduled for
                  (existing deadlines do not get changed)
        :rtype: list
        '''

    def unschedule_must_read(obj=None, userids=None):
        '''Remove a all open read requests created with `schedule_must_read`
        for a given object an/or userids.
        If the object has been marked as read by a user already, keep the
        `read` state and the `read_at` time, but remove scheduled_at/by and
        the deadline.


        :param obj: Object that all open requests shall be removed for
                    (can be combined with userids)
        :type obj: Content object (must be IUUID resolvable)
        :param userids: Userids of the users that open requests shall be
                        removed for (can be combined with obj)
        :type userids: List
        '''

    def who_did_not_read(obj, force_deadline=False, deadline_before=None):
        '''For an object scheduled as must-read, query which users have not
        read the object (at all, or before their personal deadline).

        This only queries for users who have been explicitly scheduled via
        the ``schedule_must_read()`` method. If no users were scheduled,
        returns an empty dictionary.

        Use `force_deadline` to filter for users that missed their deadline:

        * If set to True, returns scheduled users who did not read the object
          before the deadline. This includes users who may have read the object
          *after* the deadline.

        * If set to False, returns scheduled users who did not read the object
          at all.


        Use `deadline_before` to filter for users which have not read an object
        and having a deadline in the past.
        If given, only return scheduled users with a mustread deadline
        less than `deadline_before`.

        :param obj: Object that should be read by users
        :type obj: Content object (must be IUUID resolvable)
        :param force_deadline: Whether to ignore reads after the deadline
        :type force_deadline: Bool
        :param deadline_before: Filter for users with deadline <= this date
        :type deadline_before: datetime
        :returns: Dictionary with userids of users scheduled for reading which
                  did not read and their deadline (``{userid: deadline}``)
        :rtype: dict
        '''

    def what_to_read(context=None, userid=None, force_deadline=False,
                     deadline_before=None):
        '''Query which content items have open read requests.

        This only queries for objects who have been explicitly scheduled via
        the ``schedule_must_read()`` method.
        If no read requests have been scheduled an empty list is returned.

        If context is given, limit the result to objects located within
        this context. If context is ``None`` search within the plonesite.

        If userid is given, limit results to objects with an open read request
        for this userid.

        Use `force_deadline` to filter for users that missed their deadline:

        * If set to True, returns scheduled objects with unread requests
          or requests read *after* their deadline.

        * If set to False, returns scheduled objects with unread requests

        If deadline_before is given, limit the results to objects with read
        requests with a deadline less than deadline_before.

        :param context: Context to search for objects with open read requests
        :type context: Content object (must be IUUID resolvable)
        :param userid: Userid to search for open read requests for.
        :type userid: string
        :param force_deadline: Whether to ignore reads after the deadline
        :type force_deadline: Bool
        :param deadline_before: Filter for objects with deadlines <= this date
        :type deadline_before: datetime
        :returns: List of content objects with open read requests
        :rtype: list
        '''

    def get_report(context=None, include_children=True, userid=None,
                   start_date=None):
        '''Return all mustread database entries for context.
        (useful for exporting data or displaying detailed reports)

        If context is None, defaults to plone site.

        If include_children is ``True`` (which is the default), include
        mustread records for child-objects (path starts with context's path).

        If userid is given, only return entries for this user

        If start_date is given, only return entries created after start_date
        (``scheduled_at`` or ``read_at`` >= ``start_date``

        :param context: Context to create mustread report on
        :type context: Content object (must be IUUID resolvable)
        :param include_children: Whether to include child-objects of context
        :type include_children: Bool
        :param userid: only report records for specified user
        :type userid: string
        :param start_date: Filter out entries older than start_date
        :type start_at: datetime
        :returns: List of dictionaries, each representing a mustread record
                  ``[{userid, uid, status, read_at, deadline, scheduled_at,
                      type, path, ...}]``
        :rtype: Generator
        '''

    def get_report_csv(csvfile, context=None, include_children=True,
                       fieldnames=[]):
        '''Export mustread database entries for all objects within context
        in csv format to `csvfile`

        The file will contain a header line and data for all columns specified
        in `columns`.

        If context is None, defaults to plone site.

        If include_children is ``True`` (which is the default), include
        mustread records for child-objects (path starts with context's path).

        `fieldnames` can be used to define the order of columns in the report
        and which data to export.
        If fieldnames is empty, all available columns get exported.

        :param csvfile: file-like object with a`write` method that all records
                        will be written to (see csv.writer documentation)
        :type csvfile: file or stream
        :param context: Context to create mustread report on
        :type context: Content object (must be IUUID resolvable)
        :param include_children: Whether to include child-objects of context
        :type include_children: Bool
        :param fieldnames: Names of the columns to add to the csv file
        :type fieldnames: list
        '''
