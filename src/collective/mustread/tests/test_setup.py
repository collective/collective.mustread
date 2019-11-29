# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.mustread.testing import COLLECTIVE_MUSTREAD_INTEGRATION_TESTING
from Products.CMFPlone.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.mustread is properly installed."""

    layer = COLLECTIVE_MUSTREAD_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal)

    def test_product_installed(self):
        """Test if collective.mustread is installed."""
        self.assertTrue(self.installer.is_product_installed(
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
        self.installer = get_installer(self.portal)
        self.installer.uninstall_product('collective.mustread')

    def test_product_uninstalled(self):
        """Test if collective.mustread is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed(
            'collective.mustread'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveMustreadLayer is removed."""
        from collective.mustread.interfaces import \
            ICollectiveMustreadLayer
        from plone.browserlayer import utils
        self.assertNotIn(ICollectiveMustreadLayer, utils.registered_layers())
