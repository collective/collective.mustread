# -*- coding: utf-8 -*-
from collective.mustread.interfaces import ITracker
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface


class ITrackReadEnabled(Interface):
    """
    Indicator that all first reads on this object should be tracked.

    Note that this API closely shadows ..interfaces.ITracker
    """

    def mark_read(userid=None, read_at=None):
        '''Apply ..interfaces.ITracker.mark_read on context object.
        '''

    def has_read(userid=None):
        '''Apply ..interfaces.ITracker.mark_read on context object.
        '''

    def who_read():
        '''Apply ..interfaces.ITracker.mark_read on context object.
        '''


@implementer(ITrackReadEnabled)
class TrackReadEnabled(object):

    def __init__(self, context):
        self.context = context

    def mark_read(self, userid=None, read_at=None):
        '''Apply ..interfaces.ITracker.mark_read on context object.
        '''
        tracker = getUtility(ITracker)
        return tracker.mark_read(self.context, userid, read_at)

    def has_read(self, userid=None):
        '''Apply ..interfaces.ITracker.mark_read on context object.
        '''
        tracker = getUtility(ITracker)
        return tracker.has_read(self.context, userid)

    def who_read(self):
        '''Apply ..interfaces.ITracker.mark_read on context object.
        '''
        tracker = getUtility(ITracker)
        return tracker.who_read(self.context)
