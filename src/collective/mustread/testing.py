# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.mustread


class CollectiveMustreadLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.mustread)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.mustread:default')


COLLECTIVE_MUSTREAD_FIXTURE = CollectiveMustreadLayer()


COLLECTIVE_MUSTREAD_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_MUSTREAD_FIXTURE,),
    name='CollectiveMustreadLayer:IntegrationTesting'
)


COLLECTIVE_MUSTREAD_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_MUSTREAD_FIXTURE,),
    name='CollectiveMustreadLayer:FunctionalTesting'
)


COLLECTIVE_MUSTREAD_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_MUSTREAD_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveMustreadLayer:AcceptanceTesting'
)
