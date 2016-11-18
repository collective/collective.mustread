# -*- coding: utf-8 -*-
from collective.mustread import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IMaybeMustRead(model.Schema):
    """
    Choice whether this object MUST be read.

    Only makes sense in combination with a read tracking behavior.
    """

    must_read = schema.Bool(
        title=_(
            u'label_must_read_authenticated',
            default=u'All users must read this'
        ),
        required=False,
        default=False,
    )
