from mock import Mock, patch
import unittest

from contextio.lib.resources.file import File


class TestFile(unittest.TestCase):
    def setUp(self):
        self.file = File(Mock(), {"file_id": "fake_file_id"})

    def test_constructor_creates_file_object_with_all_attributes_in_keys_list(self):
        self.assertTrue(hasattr(self.file, "size"))
        self.assertTrue(hasattr(self.file, "type"))
        self.assertTrue(hasattr(self.file, "subject"))
        self.assertTrue(hasattr(self.file, "date"))
        self.assertTrue(hasattr(self.file, "date_indexed"))
        self.assertTrue(hasattr(self.file, "addresses"))
        self.assertTrue(hasattr(self.file, "person_info"))
        self.assertTrue(hasattr(self.file, "file_name"))
        self.assertTrue(hasattr(self.file, "file_name_structure"))
        self.assertTrue(hasattr(self.file, "body_section"))
        self.assertTrue(hasattr(self.file, "file_id"))
        self.assertTrue(hasattr(self.file, "supports_preview"))
        self.assertTrue(hasattr(self.file, "is_embedded"))
        self.assertTrue(hasattr(self.file, "content_disposition"))
        self.assertTrue(hasattr(self.file, "content_id"))
        self.assertTrue(hasattr(self.file, "message_id"))
        self.assertTrue(hasattr(self.file, "email_message_id"))
        self.assertTrue(hasattr(self.file, "gmail_message_id"))
        self.assertTrue(hasattr(self.file, "gmail_thread_id"))

    @patch("contextio.lib.resources.file.File._request_uri")
    def test_get_content_calls_request_uri_with_correct_arguments(self, mock_request):
        file = File(Mock(), {"file_id": "fake_file_id"})

        file.get_content()

        mock_request.assert_called_with("content", headers={})

    @patch("contextio.lib.resources.file.File._request_uri")
    def test_get_content_calls_request_uri_with_correct_arguments_when_download_link_is_True(self, mock_request):
        file = File(Mock(), {"file_id": "fake_file_id"})

        file.get_content(download_link=True)

        mock_request.assert_called_with("content", headers={"Accept": "text/uri-list"})

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_related_returns_a_list_of_File_objects(self, mock_request):
        mock_request.return_value = [{"file_id": "related_file_id"}]

        related_files = self.file.get_related()

        self.assertEqual(1, len(related_files))
        self.assertIsInstance(related_files[0], File)

