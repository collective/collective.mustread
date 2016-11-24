# -*- coding: utf-8 -*-
from collective.mustread.behaviors.track import ITrackReadEnabled
from Products.Five.browser import BrowserView


class Hit(BrowserView):
    '''Helper view to mark an ITrackReadEnabled context as read
    by current user.'''

    def __call__(self):
        ITrackReadEnabled(self.context).mark_read()
        return '%s Marked Read' % '/'.join(self.context.getPhysicalPath())


class HasRead(BrowserView):
    '''Helper view to inspect ITrackReadEnabled read status for current user'''
    def __call__(self):
        status = ITrackReadEnabled(self.context).has_read()
        return 'Read: %s' % status
