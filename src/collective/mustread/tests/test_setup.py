# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.mustread.testing import COLLECTIVE_MUSTREAD_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.mustread is properly installed."""

    layer = COLLECTIVE_MUSTREAD_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.mustread is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.mustread'))

    def test_browserlayer(self):
        """Test that ICollectiveMustreadLayer is registered."""
        from collective.mustread.interfaces import (
            ICollectiveMustreadLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveMustreadLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_MUSTREAD_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.mustread'])

    def test_product_uninstalled(self):
        """Test if collective.mustread is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.mustread'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveMustreadLayer is removed."""
        from collective.mustread.interfaces import \
            ICollectiveMustreadLayer
        from plone.browserlayer import utils
        self.assertNotIn(ICollectiveMustreadLayer, utils.registered_layers())
