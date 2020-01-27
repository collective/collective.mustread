# -*- coding: utf-8 -*-
from collective.mustread.testing import COLLECTIVE_MUSTREAD_INTEGRATION_TESTING
from plone import api
from Products.GenericSetup.upgrade import listUpgradeSteps

import unittest


class TestSetup(unittest.TestCase):
    '''Test that collective.mustread is properly installed.'''

    layer = COLLECTIVE_MUSTREAD_INTEGRATION_TESTING

    def test_to1002(self):
        pt = api.portal.get_tool('portal_types')
        pt['News Item'].behaviors = (
            'collective.mustread.behaviors.maybe.IMaybeMustRead',
            'collective.mustread.behaviors.track.ITrackReadEnabled',
        )
        ps = api.portal.get_tool('portal_setup')
        upgrade_steps = listUpgradeSteps(
            ps, 'collective.mustread:default', '1001'
        )
        for upgrade_step in upgrade_steps:
            upgrade_step['step'].doStep(ps)
        self.assertTupleEqual(
            pt['News Item'].behaviors,
            (
                'collective.mustread.maybe_must_read',
                'collective.mustread.track_read_enabled',
            )
        )
