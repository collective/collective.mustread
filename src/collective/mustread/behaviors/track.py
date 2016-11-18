# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.interface import Interface


class ITrackReads(Interface):
    """
    Track all first reads on this object for every authenticated user.
    """


@implementer(ITrackReads)
class TrackReads(object):
    pass
