"""
Test for search performance
"""

import os
import time

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from localhost.core.factories import PropertyFactory


class SearchPerformanceTest(TestCase):
    """
    Used to test the performance of a search in the database.
    The size of the database is determined by the 'BATCH_SIZE' environment
    variable the caller sets.
    """

    @classmethod
    def setUpTestData(cls):
        size = int(os.getenv('BATCH_SIZE'))
        print('Generating batch...')
        cls.properties = PropertyFactory.create_batch(size)
        print('Finished.')

    def search(self):
        """
        Performs a search on the database
        """
        lat, lng = settings.DEFAULT_SEARCH_COORD
        url = f'{reverse("core:search_results")}?lat={lat}&lng={lng}'
        self.client.get(url)

    def test_search_performance(self):
        """
        Testing the performance of a search on the database
        """
        print('Performing search...')
        time_start = time.clock()
        self.search()
        time_taken = time.clock() - time_start
        print('Finished.')
        print('Search took: ' + str(time_taken))
