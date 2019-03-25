# coding=utf-8
from collective.mustread import db
from collective.mustread.interfaces import IMustReadSettings
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import logging


logger = logging.getLogger('collective.mustread')


def fix_registry_records(context):
    ''' Fix the registy records
    '''
    registry = getUtility(IRegistry)
    registry.registerInterface(IMustReadSettings)


def update_dbschema(context):
    '''adds new columns to mustread database.

    we rely on a sqlite database here, for a database agnostic solution
    we'd need to use a dedicated migration tool (see
    http://docs.sqlalchemy.org/en/latest/core/metadata.html#altering-schemas-through-migrations)
    '''

    record = api.portal.get_registry_record(
        'collective.mustread.interfaces.IMustReadSettings.connectionstring')
    if record and not record.startswith('sqlite://'):
        logger.warn('database migration is only tested for sqlite databases')

    engine = db.getEngine()
    for statement in (
        'ALTER TABLE mustread ADD column scheduled_by VARCHAR(255);',
        'ALTER TABLE mustread ADD column scheduled_at DATETIME;'
    ):
        try:
            engine.execute(statement)
        except Exception:
            logger.exception('Failed to execute %r', statement)

    # drop column is not supported by sqlite
    # we'd need to rename and copy the database
    # (see http://stackoverflow.com/a/10581330/810427)
    # i'd suggest to keep the columns in existing tables
    # and simply remove them from the orm-model.
    # engine.execute('ALTER TABLE mustread DROP column site_name;')
    # engine.execute('ALTER TABLE mustread DROP column title;')
    # engine.execute('ALTER TABLE mustread DROP column info;')
