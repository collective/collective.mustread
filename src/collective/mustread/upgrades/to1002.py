# coding=utf-8
from plone import api
from plone.dexterity.interfaces import IDexterityFTI

import logging


logger = logging.getLogger('collective.mustread')


def move_dotted_to_named_behaviors(context):
    """ https://github.com/plone/plone.app.upgrade/blob/master/plone/app/upgrade/v52/alphas.py#L58  # noqa: E501
    """
    mapping = {
        'collective.mustread.behaviors.maybe.IMaybeMustRead': 'collective.mustread.maybe_must_read',  # noqa: E501
        'collective.mustread.behaviors.track.ITrackReadEnabled': 'collective.mustread.track_read_enabled',  # noqa: E501
    }

    ptt = api.portal.get_tool("portal_types")
    ftis = (fti for fti in ptt.objectValues() if IDexterityFTI.providedBy(fti))
    for fti in ftis:
        behaviors = []
        change_needed = False
        for behavior in fti.behaviors:
            if behavior in mapping:
                behavior = mapping[behavior]
                change_needed = True
            behaviors.append(behavior)
        if change_needed:
            fti.behaviors = tuple(behaviors)

    logger.info("Done moving dotted to named behaviors.")
