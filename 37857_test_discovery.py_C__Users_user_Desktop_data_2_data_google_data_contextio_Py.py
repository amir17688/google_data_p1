import unittest
from mock import Mock

from contextio.lib.resources.discovery import Discovery


class TestDiscovery(unittest.TestCase):
    def setUp(self):
        self.discovery = Discovery(Mock(), {})

    def test_constructor_creates_discovery_object_with_all_attributes_in_keys_list(self):
        self.assertTrue(hasattr(self.discovery, 'email'))
        self.assertTrue(hasattr(self.discovery, 'found'))
        self.assertTrue(hasattr(self.discovery, 'type'))
        self.assertTrue(hasattr(self.discovery, 'imap'))
        self.assertTrue(hasattr(self.discovery, 'documentation'))
