# coding=utf-8
from collective.mustread.interfaces import IMustReadSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def fix_registry_records(context):
    ''' Fix the registy records
    '''
    registry = getUtility(IRegistry)
    registry.registerInterface(IMustReadSettings)
