from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from localhost.core.factories import PropertyFactory


class SearchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.properties = PropertyFactory.create_batch(10000)

    def test_search(self):
        lat, lng = settings.DEFAULT_SEARCH_COORD
        url = f'{reverse("core:search_results")}?lat={lat}&lng={lng}'
        response = self.client.get(url)
        self.assertEqual(response.context_data['object_list'].count(), 20)
