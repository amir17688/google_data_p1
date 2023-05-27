import unittest
from mock import Mock, patch

from contextio.lib.resources.connect_token import ConnectToken
from contextio.lib.resources.folder import Folder
from contextio.lib.resources.source import Source


class TestSource(unittest.TestCase):
    def setUp(self):
        self.source = Source(Mock(spec=[]), {"label": "foobar"})

    def test_constructor_creates_message_object_with_all_attributes_in_keys_list(self):
        self.assertTrue(hasattr(self.source, "username"))
        self.assertTrue(hasattr(self.source, "status"))
        self.assertTrue(hasattr(self.source, "type"))
        self.assertTrue(hasattr(self.source, "label"))
        self.assertTrue(hasattr(self.source, "use_ssl"))
        self.assertTrue(hasattr(self.source, "resource_url"))
        self.assertTrue(hasattr(self.source, "server"))
        self.assertTrue(hasattr(self.source, "port"))

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_delete_connect_token_calls_request_uri_with_correct_args(self, mock_request):
        self.source.delete_connect_token("fake_token_id")

        mock_request.assert_called_with("connect_tokens/fake_token_id", method="DELETE")

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_connect_token_returns_a_ConnectToken(self, mock_request):
        mock_request.return_value = {"token": "fake_token_id"}
        response = self.source.get_connect_token("fake_token_id")

        mock_request.is_called_with("connect_tokens/fake_token_id")
        self.assertIsInstance(response, ConnectToken)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_connect_tokens_returns_a_list_of_ConnectTokens(self, mock_request):
        mock_request.return_value = [{"token": "fake_token_id"}, {"token": "fake_token_id_2"}]
        response = self.source.get_connect_tokens()

        mock_request.is_called_with("connect_tokens/fake_token_id")
        self.assertEqual(2, len(response))
        self.assertIsInstance(response[0], ConnectToken)
        self.assertIsInstance(response[1], ConnectToken)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_post_calls_request_uri_with_correct_args(self, mock_request):
        mock_request.return_value = {"success": True}
        response = self.source.post_connect_token(callback_url="http://some.url")

        mock_request.is_called_with(
            "connect_tokens", method="POST", params={"callback_url": "http://some.url"})
        self.assertEqual({"success": True}, response)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_folder_returns_a_list_of_Folders(self, mock_request):
        mock_request.return_value = [{"name": "folder_name"}, {"name": "folder_name_2"}]
        response = self.source.get_folders()

        mock_request.is_called_with("folders")
        self.assertEqual(2, len(response))
        self.assertIsInstance(response[0], Folder)
        self.assertIsInstance(response[1], Folder)


    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_sync_returns_a_dictionary(self, mock_request):
        mock_request.return_value = {"foo": "bar"}
        response = self.source.get_sync()

        mock_request.assert_called_with("sync")
        self.assertEqual({"foo": "bar"}, response)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_post_sync_calls_request_uri_with_correct_args(self, mock_request):
        mock_request.return_value = {"foo": "bar"}
        response = self.source.post_sync()

        mock_request.assert_called_with("sync", method="POST")
        self.assertEqual({"foo": "bar"}, response)
