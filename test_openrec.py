import requests
import unittest
from unittest.mock import patch, Mock
from typing import List
from openrec import (
    LiveInfo,
    liveinfo_list_from_api,
    info_list_post_discord
)

class TestLiveInfo(unittest.TestCase):
    def test_live_info_creation(self):
        info = LiveInfo(
            title="テスト配信",
            channel_id="test123",
            nickname="テスト太郎"
        )
        
        self.assertEqual(info.title, "テスト配信")
        self.assertEqual(info.channel_id, "test123")
        self.assertEqual(info.nickname, "テスト太郎")
        
        expected_content = "テスト配信:テスト太郎(test123)"
        self.assertEqual(info.to_content(), expected_content)

class TestLiveInfoFromApi(unittest.TestCase):
    def setUp(self):
        self.test_url = "https://api.test.com/endpoint"
        self.test_response = [
            {
                "title": "配信1",
                "channel": {
                    "id": "ch1",
                    "nickname": "配信者1"
                }
            },
            {
                "title": "配信2",
                "channel": {
                    "id": "ch2",
                    "nickname": "配信者2"
                }
            }
        ]

    @patch('requests.get')
    def test_successful_api_call(self, mock_get):
        # 正常系のAPIレスポンスをモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.test_response
        mock_get.return_value = mock_response

        result = liveinfo_list_from_api(self.test_url)

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], LiveInfo)
        self.assertEqual(result[0].title, "配信1")
        self.assertEqual(result[0].channel_id, "ch1")
        self.assertEqual(result[0].nickname, "配信者1")

    @patch('requests.get')
    def test_empty_api_response(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = liveinfo_list_from_api(self.test_url)
        self.assertEqual(len(result), 0)

    @patch('requests.get')
    def test_api_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        with self.assertRaises(requests.exceptions.RequestException):
            liveinfo_list_from_api(self.test_url)

class TestInfoListPostDiscord(unittest.TestCase):
    def setUp(self):
        self.webhook_url = "https://discord.webhook.test"
        self.api_url = "https://api.test.com/endpoint"
        self.id_list = ["ch1", "ch3"]
        self.lock_path = "/tmp/test.lock"
        
        self.test_api_response = [
            {
                "title": "配信1",
                "channel": {
                    "id": "ch1",
                    "nickname": "配信者1"
                }
            },
            {
                "title": "配信2",
                "channel": {
                    "id": "ch2",
                    "nickname": "配信者2"
                }
            }
        ]

    @patch('requests.post')
    @patch('requests.get')
    @patch('openrec.post_discord_if_not_same')
    @patch('openrec.remove_lockfile')
    def test_matching_channel_post(self, mock_remove_lockfile, mock_post_discord, mock_get, mock_post):
        # APIレスポンスのモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.test_api_response
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response

        info_list_post_discord(
            self.webhook_url,
            self.api_url,
            self.id_list,
            self.lock_path
        )

        # Discord投稿の検証
        mock_post_discord.assert_called_once()
        mock_remove_lockfile.assert_not_called()
        call_args = mock_post_discord.call_args[0]
        self.assertIn("配信1:配信者1(ch1)", call_args[0])

    @patch('requests.post')
    @patch('requests.get')
    @patch('openrec.post_discord_if_not_same')
    @patch('openrec.remove_lockfile')
    def test_no_matching_channel(self, mock_remove_lockfile, mock_post_discord, mock_get, mock_post):
        # マッチしないチャンネルIDでテスト
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.test_api_response
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response

        info_list_post_discord(
            self.webhook_url,
            self.api_url,
            ["ch99"],  # マッチしないID
            self.lock_path
        )

        mock_post_discord.assert_not_called()
        mock_remove_lockfile.assert_called_once_with(self.lock_path)

    @patch('requests.get')
    def test_api_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        with self.assertRaises(requests.exceptions.RequestException):
            info_list_post_discord(
                self.webhook_url,
                self.api_url,
                self.id_list,
                self.lock_path
            )

if __name__ == '__main__':
    unittest.main()
