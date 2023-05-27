from mock import Mock, patch
import unittest

from contextio.lib.resources.account import Account
from contextio.lib.resources.contact import Contact
from contextio.lib.resources.connect_token import ConnectToken
from contextio.lib.resources.email_address import EmailAddress
from contextio.lib.resources.message import Message
from contextio.lib.resources.source import Source
from contextio.lib.resources.thread import Thread
from contextio.lib.resources.webhook import WebHook
from contextio.lib.resources.file import File
from contextio.lib.helpers import ArgumentError

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account(Mock(spec=[]), {"id": "fake_id"})

    @patch("contextio.lib.resources.base_resource.BaseResource.post")
    def test_post_updates_first_and_last_name(self, mock_post):
        mock_post.return_value = True
        params = {
            "first_name": "Leeroy",
            "last_name": "Jenkins"
        }

        response = self.account.post(**params)

        self.assertEqual(self.account.first_name, "Leeroy")
        self.assertEqual(self.account.last_name, "Jenkins")
        mock_post.assert_called_with(all_args=['first_name', 'last_name'], params=params)
        self.assertTrue(response)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_connect_tokens_returns_list_of_connect_tokens(self, mock_request):
        mock_request.return_value = [{"token": "fake_token", "account": {"id": "foobar"}}]

        account_connect_tokens = self.account.get_connect_tokens()

        self.assertEqual(1, len(account_connect_tokens))
        self.assertIsInstance(account_connect_tokens[0], ConnectToken)
        self.assertIsInstance(account_connect_tokens[0].account, Account)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_contacts_returns_list_of_contacts(self, mock_get):
        mock_get.return_value = {"matches": [{"email": "foo@bar.com"}]}

        account_contacts = self.account.get_contacts()

        self.assertEqual(1, len(account_contacts))
        self.assertIsInstance(account_contacts[0], Contact)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_email_addresses_returns_list_of_EmailAddresses(self, mock_request):
        mock_request.return_value = [{"email": "fake_token"}]

        response = self.account.get_email_addresses()

        self.assertIsInstance(response[0], EmailAddress)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_files_returns_list_of_Files(self, mock_request):
        mock_request.return_value = [{"file_id": "foobar"}]

        response = self.account.get_files()

        self.assertIsInstance(response[0], File)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_messages_returns_list_of_Messages(self, mock_request):
        mock_request.return_value = [{"message_id": "foobar"}]

        response = self.account.get_messages()

        self.assertIsInstance(response[0], Message)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_sources_returns_list_of_Sources(self, mock_request):
        mock_request.return_value = [{"label": "foobar"}]

        response = self.account.get_sources()

        self.assertIsInstance(response[0], Source)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_sync_returns_a_dictionary(self, mock_request):
        mock_request.return_value = {"foo": "bar"}

        response = self.account.get_sync()

        self.assertIsInstance(response, dict)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_threads_returns_list_of_Threads(self, mock_request):
        mock_request.return_value = ["foo/bar"]

        response = self.account.get_threads()

        self.assertIsInstance(response[0], Thread)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_webhooks_returns_list_of_WebHooks(self, mock_request):
        mock_request.return_value = [{"webhook_id": "foobar"}]

        response = self.account.get_webhooks()

        self.assertIsInstance(response[0], WebHook)

    def test_post_connect_token_requires_callback_url(self):
        with self.assertRaises(ArgumentError):
            self.account.post_connect_token()

    def test_post_email_address_requires_email_address(self):
        with self.assertRaises(ArgumentError):
            self.account.post_email_address()

    @patch("contextio.lib.resources.base_resource.BaseResource.post")
    def test_post_email_address_returns_EmailAddress(self, mock_post):
        mock_post.return_value = {"email": "fake@email.com"}

        email_address = self.account.post_email_address(email_address="fake@email.com")

        self.assertIsInstance(email_address, EmailAddress)

    @patch("contextio.lib.resources.base_resource.BaseResource.post")
    def test_post_message_requires_certain_args(self, mock_post):
        all_args = [
            "dst_source", "dst_folder", "message", "flag_seen", "flag_answered", "flag_flagged",
            "flag_deleted", "flag_draft"
        ]
        req_args = ["dst_source", "dst_folder", "message"]

        self.account.post_message()

        mock_post.assert_called_with(
            all_args=all_args, headers={"Content-Type": "multipart/form-data"},
            params={},
            required_args=req_args,
            return_bool=False,
            uri="messages")

    @patch("contextio.lib.resources.base_resource.BaseResource.post")
    def test_post_source_requires_certain_args(self, mock_post):
        all_args = [
            'email', 'server', 'username', 'port', 'type', 'use_ssl',
            'origin_ip', 'expunge_on_deleted_flag', 'sync_all_folders',
            'sync_folders', 'sync_flags', 'raw_file_list', 'password',
            'provider_refresh_token', 'provider_consumer_key',
            'callback_url', 'status_callback_url'
        ]
        req_args = ['email', 'server', 'username', 'port', 'type', 'use_ssl']

        self.account.post_source()

        mock_post.assert_called_with(
            return_bool=False,
            all_args=all_args,
            params={"use_ssl": 1, "type": "IMAP", "port": 993},
            required_args=req_args,
            uri="sources")

    @patch("contextio.lib.resources.base_resource.BaseResource.post")
    def test_post_source_returns_Source_object(self, mock_post):
        mock_post.return_value = {"label": "foobar"}
        source = self.account.post_source()

        self.assertIsInstance(source, Source)

    @patch("contextio.lib.resources.base_resource.BaseResource.post")
    def test_post_source_returns_False_if_creation_failed(self, mock_post):
        mock_post.return_value = {"success": False}
        response = self.account.post_source()

        self.assertFalse(response)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_post_sync_calls_request_uri_with_correct_args(self, mock_request):
        self.account.post_sync()

        mock_request.assert_called_with("sync", method="POST")

    def test_post_webhook_requires_args(self):
        with self.assertRaises(ArgumentError):
            self.account.post_webhook()

    @patch("contextio.lib.resources.base_resource.BaseResource.post")
    def test_post_webhook_returns_WebHook_object(self, mock_post):
        mock_post.return_value = {"success": True, "webhook_id": "foobar"}
        webhook = self.account.post_webhook()

        self.assertIsInstance(webhook, WebHook)

    @patch("contextio.lib.resources.base_resource.BaseResource.post")
    def test_post_webhook_returns_False_if_creation_failed(self, mock_post):
        mock_post.return_value = {"success": False}
        response = self.account.post_webhook()

        self.assertFalse(response)

