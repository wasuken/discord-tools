import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
from common import (
    read_config,
    post_discord,
    post_discord_if_not_same,
    post_discord_with_file,
    remove_lockfile,
)

class TestCommon(unittest.TestCase):
    def setUp(self):
        # テスト用の設定
        self.test_config = {
            "webhook_url": "https://discord.com/api/webhooks/test",
            "other_setting": "value"
        }
        self.test_message = "Test Message"
        self.test_webhook_url = "https://discord.com/api/webhooks/test"

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_read_config_exists(self, mock_file, mock_exists):
        # 設定ファイルが存在する場合のテスト
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(self.test_config)
        
        result = read_config()
        self.assertEqual(result, self.test_config)

    @patch('os.path.exists')
    def test_read_config_not_exists(self, mock_exists):
        # 設定ファイルが存在しない場合のテスト
        mock_exists.return_value = False
        
        result = read_config()
        self.assertIsNone(result)

    @patch('requests.post')
    def test_post_discord(self, mock_post):
        # Discord投稿のテスト
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = post_discord(self.test_message, self.test_webhook_url)
        
        mock_post.assert_called_once_with(
            self.test_webhook_url,
            data={"content": self.test_message}
        )
        self.assertEqual(response.status_code, 200)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('requests.post')
    def test_post_discord_if_not_same_new_message(self, mock_post, mock_file, mock_exists):
        # 新しいメッセージの場合のテスト
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = "Different message"
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        result = post_discord_if_not_same(self.test_message, self.test_webhook_url, '/tmp/test.lock')
        
        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('requests.post')
    def test_post_discord_if_not_same_duplicate(self, mock_post, mock_file, mock_exists):
        # 重複メッセージの場合のテスト
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = self.test_message

        result = post_discord_if_not_same(self.test_message, self.test_webhook_url, '/tmp/test.lock')
        
        self.assertFalse(result)
        mock_post.assert_not_called()

    @patch('os.path.exists')
    @patch('os.remove')
    def test_remove_lockfile(self, mock_remove, mock_exists):
        # ロックファイル削除のテスト
        mock_exists.return_value = True
        
        lock_path = '/tmp/openrec.lock'
        remove_lockfile(lock_path)
        
        mock_remove.assert_called_once_with(lock_path)

    @patch('requests.post')
    def test_post_discord_with_file(self, mock_post):
        # ファイル付きのDiscord投稿のテスト
        test_file_path = "test.txt"
        test_file_content = b"test content"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with patch('builtins.open', mock_open(read_data=test_file_content)):
            response = post_discord_with_file(
                self.test_message,
                self.test_webhook_url,
                test_file_path
            )

        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
