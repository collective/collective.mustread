# -*- coding: utf-8 -*-
from collective.mustread.behaviors.track import ITrackReadEnabled
from Products.Five.browser import BrowserView


class Hit(BrowserView):

    def __call__(self):
        ITrackReadEnabled(self.context).mark_read()
        return '%s Marked Read' % '/'.join(self.context.getPhysicalPath())
