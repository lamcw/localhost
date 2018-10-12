"""
Test for search performance.
"""

import os
import time

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from localhost.core.factories import PropertyFactory


class SearchPerformanceTest1000(TestCase):
    """
    Used to test the performance of a search in the database.
    """
    fixtures = ['testdata', 'properties1000']

    def search(self):
        """
        Performs a search on the database
        """
        lat, lng = settings.DEFAULT_SEARCH_COORD
        url = f'{reverse("core:search-results")}?lat={lat}&lng={lng}'
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
        print('Search took: ' + str(time_taken) + '.')

class SearchPerformanceTest10000(TestCase):
    """
    Used to test the performance of a search in the database.
    """
    fixtures = ['testdata', 'properties10000']

    def search(self):
        """
        Performs a search on the database
        """
        lat, lng = settings.DEFAULT_SEARCH_COORD
        url = f'{reverse("core:search-results")}?lat={lat}&lng={lng}'
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
        print('Search took: ' + str(time_taken) + '.')

class SearchPerformanceTest100000(TestCase):
    """
    Used to test the performance of a search in the database.
    """
    fixtures = ['testdata', 'properties100000']

    def search(self):
        """
        Performs a search on the database
        """
        lat, lng = settings.DEFAULT_SEARCH_COORD
        url = f'{reverse("core:search-results")}?lat={lat}&lng={lng}'
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
        print('Search took: ' + str(time_taken) + '.')

class SearchPerformanceTest1000000(TestCase):
    """
    Used to test the performance of a search in the database.
    """
    fixtures = ['testdata', 'properties1000000']

    def search(self):
        """
        Performs a search on the database
        """
        lat, lng = settings.DEFAULT_SEARCH_COORD
        url = f'{reverse("core:search-results")}?lat={lat}&lng={lng}'
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
        print('Search took: ' + str(time_taken) + '.')
