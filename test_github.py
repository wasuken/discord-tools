import unittest
from unittest.mock import patch, Mock, mock_open
from datetime import datetime
import json
import os
from github import (
    generate_calendar_image,
    get_push_events,
)

class TestGitHubActivity(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            "github": {
                "username": "test_user",
                "webhook": "https://discord.webhook.test"
            }
        }
        self.test_events = [
            {
                "type": "PushEvent",
                "created_at": "2024-01-01T10:00:00Z"
            },
            {
                "type": "PushEvent",
                "created_at": "2024-01-15T15:30:00Z"
            },
            {
                "type": "OtherEvent",
                "created_at": "2024-01-20T12:00:00Z"
            }
        ]

    @patch('requests.get')
    def test_get_push_events(self, mock_get):
        # GitHub APIレスポンスのモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.test_events
        mock_get.return_value = mock_response

        # テスト実行
        result = get_push_events("test_user")

        # 検証
        mock_get.assert_called_once_with(
            "https://api.github.com/users/test_user/events"
        )
        self.assertEqual(len(result), 2)  # PushEventのみがフィルタされている
        self.assertTrue(all(event['type'] == 'PushEvent' for event in result))

    @patch('requests.get')
    def test_get_push_events_error(self, mock_get):
        # エラーレスポンスのモック
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # テスト実行
        result = get_push_events("test_user")

        # 検証
        self.assertEqual(result, "Error: 404")

    def test_generate_calendar_image(self):
        # テスト用の日付リスト
        test_dates = [
            datetime(2024, 1, 1),
            datetime(2024, 1, 15)
        ]
        test_image_path = "test_calendar.png"

        # 関数実行
        generate_calendar_image(test_dates, test_image_path)

        # 検証
        self.assertTrue(os.path.exists(test_image_path))

    def tearDown(self):
        # テスト後のクリーンアップ
        if os.path.exists('calendar.png'):
            os.remove('calendar.png')
        if os.path.exists('test_calendar.png'):
            os.remove('test_calendar.png')

if __name__ == '__main__':
    unittest.main()
