# -*- coding: utf-8 -*-
from collective.mustread.behaviors.maybe import IMaybeMustRead
from collective.mustread.behaviors.track import ITrackReadEnabled
from collective.mustread.db import getSession
from collective.mustread.interfaces import IMustReadSettings
from collective.mustread.models import Base
from collective.mustread.models import MustRead
from collective.mustread.tracker import Tracker
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.behavior.interfaces import IBehavior
from plone.behavior.interfaces import IBehaviorAssignable
from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry
from plone.testing import z2
from tempfile import mkstemp
from zope.component import adapter
from zope.component import getUtility
from zope.component import provideAdapter
from zope.component import queryUtility
from zope.interface import implementer

import collective.mustread
import os
import unittest


# http://docs.plone.org/external/plone.app.dexterity/docs/behaviors/testing-behaviors.html
@adapter(IDexterityContent)
@implementer(IBehaviorAssignable)
class TestingAssignable(object):

    enabled = [ITrackReadEnabled, IMaybeMustRead]

    def __init__(self, context):
        self.context = context

    def supports(self, behavior_interface):
        return behavior_interface in self.enabled

    def enumerateBehaviors(self):
        for e in self.enabled:
            yield queryUtility(IBehavior, name=e.__identifier__)


class CollectiveMustreadLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.mustread)
        provideAdapter(TestingAssignable)

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


class tempDb(object):

    registry_key = '{iface}.connectionstring'.format(
        iface=IMustReadSettings.__identifier__
    )
    session = None

    def __init__(self):
        _, self.tempfilename = mkstemp()
        self.registry = registry = getUtility(IRegistry)
        registry[self.registry_key] = (
            u'sqlite:///%s' % (self.tempfilename)
        )
        self.session = getSession()
        Base.metadata.create_all(self.session.bind.engine)

    def __del__(self):
        try:
            os.remove(self.tempfilename)
        except OSError:
            # __del__ is called more than once...
            pass

    @property
    def reads(self):
        return self.session.query(MustRead).all()


class FunctionalBaseTestCase(unittest.TestCase):

    layer = COLLECTIVE_MUSTREAD_FUNCTIONAL_TESTING

    def setUp(self):
        self.db = tempDb()  # auto teardown via __del__
        self.portal = self.layer['portal']
        self.request = self.layer['request'].clone()
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.page = api.content.create(type='Document',
                                       id='page',
                                       title='Page',
                                       container=self.portal)
        self.tracker = Tracker()
