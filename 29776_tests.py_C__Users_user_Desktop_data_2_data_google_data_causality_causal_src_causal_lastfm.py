"""Tests for last.fm app."""

from causal.lastfm.service import ServiceHandler
from causal.main.models import UserService
from django.test import TestCase
from django.utils import simplejson
import os

try:
    import wingdbstub
except ImportError:
    pass

class TestLastfmService(TestCase):
    """Test the module with fixtures.
    """

    def setUp(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.handler = ServiceHandler(model_instance=UserService())

    def tearDown(self):
        pass

    def _loadJson(self, name):
        return simplejson.load(file(os.path.join(self.path, 'test_data', name)))

    def test_convert_recent_tracks_json(self):
        """Test the method for converting a json feed of recent
        tracks into ServiceItems.
        """

        json = self._loadJson('recent_tracks.json')

        service_items = self.handler._convert_recent_tracks_json(json)

        self.assertEqual(len(service_items), 10)

    def test_convert_recent_tracks_json_no_recent_tracks(self):
        """Check it deals with no recent tracks.
        """

        json = self._loadJson('no_recent_tracks.json')

        service_items = self.handler._convert_recent_tracks_json(json)

        self.assertEqual(len(service_items), 0)

    def test_convert_recent_tracks_json_unknown_user(self):
        """Check it deals correctly with an unknown username.
        """

        json = self._loadJson('unknown_user.json')

        service_items = self.handler._convert_recent_tracks_json(json)

        self.assertEqual(len(service_items), 0)

    def test_convert_top_artists(self):
        """Check we can convert the top_artists json without issue.
        """

        json = self._loadJson('top_artists.json')

        service_items = self.handler._convert_top_artists_json(json)

        self.assertEqual(len(service_items), 50)

    def test_convert_top_artists_unknown_user(self):
        """Check we deal with an unknown user without issue.
        """

        json = self._loadJson('top_artists_unknown_user.json')

        service_items = self.handler._convert_top_artists_json(json)

        self.assertEqual(len(service_items), 0)

    def test_convert_top_artists_none(self):
        """Check we deal with a user without any top artists.
        """

        json = self._loadJson('top_artists_none.json')

        service_items = self.handler._convert_top_artists_json(json)

        self.assertEqual(len(service_items), 0)