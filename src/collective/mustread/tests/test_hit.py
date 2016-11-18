# -*- coding: utf-8 -*-
from collective.mustread.testing import FunctionalBaseTestCase
from plone import api
from plone.app.testing import TEST_USER_ID


class TestHit(FunctionalBaseTestCase):

    def test_hit(self):
        self.assertEqual(self.db.reads, [])
        view = api.content.get_view(name='mustread-hit',
                                    context=self.page,
                                    request=self.request)
        view()
        self.assertEqual(self.db.reads[-1].status, 'read')
        self.assertEqual(self.db.reads[-1].userid, TEST_USER_ID)
