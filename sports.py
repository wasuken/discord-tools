import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from common import post_discord, read_config

# Premier League competition ID
PREMIER_LEAGUE_ID = 2021

# UTCからJSTに変換する関数
def convert_to_jst(utc_time_str):
    # UTCタイムをパース
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    # タイムゾーンをUTCに設定
    utc_time = utc_time.replace(tzinfo=timezone.utc)
    # JSTはUTC+9時間
    jst_time = utc_time + timedelta(hours=9)
    return jst_time

# 曜日の日本語表記を取得する
def get_japanese_weekday(date):
    weekdays = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    return weekdays[date.weekday()]

# スケジュール表示を整形する関数
def format_schedule(matches_by_date, start_date, end_date):
    # 週間スケジュールのヘッダー
    header = f"====== プレミアリーグ 週間スケジュール ({start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}) ======"
    
    # メッセージを組み立てる
    message_parts = [header, ""]
    
    # 一週間の日付を列挙
    current_date = start_date.date()
    for _ in range(7):
        jp_weekday = get_japanese_weekday(current_date)
        date_str = current_date.strftime('%Y/%m/%d')
        
        # 日付ごとのヘッダーを追加
        message_parts.append(f"【{jp_weekday}】{date_str}")
        
        # その日の試合があれば表示、なければ「予定された試合はありません」と表示
        if current_date in matches_by_date:
            # 時間順にソート
            sorted_matches = sorted(matches_by_date[current_date], key=lambda x: x['time'])
            for match in sorted_matches:
                message_parts.append(f"{match['time']}  {match['home']} vs {match['away']}")
        else:
            message_parts.append("予定された試合はありません")
        
        message_parts.append("")  # 空行を追加
        current_date += timedelta(days=1)
    
    # 最終的なメッセージを作成
    return "\n".join(message_parts)

if __name__ == '__main__':
    # 設定ファイルの読み込み
    user_config = read_config()
    
    # 日付の計算
    today = datetime.today()
    week_later = today + timedelta(days=7)
    date_from = today.strftime('%Y-%m-%d')
    date_to = week_later.strftime('%Y-%m-%d')

    # API request URL for matches in the next week
    url = f"https://api.football-data.org/v4/competitions/{PREMIER_LEAGUE_ID}/matches"

    # Set up the headers including the API key
    headers = {
        'X-Auth-Token': user_config['football']['api_key']
    }

    # APIリクエストのパラメータ設定
    params = {
        'dateFrom': date_from, 
        'dateTo': date_to
    }

    try:
        # Make the request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # エラーハンドリングを追加
        
        # Parse and format match data
        matches = response.json().get('matches', [])
        
        # 日付ごとに試合をグループ化
        matches_by_date = defaultdict(list)
        
        if matches:
            for match in matches:
                home_team = match['homeTeam']['name']
                away_team = match['awayTeam']['name']
                
                # 試合日時をJSTに変換
                match_datetime = convert_to_jst(match['utcDate'])
                match_date = match_datetime.date()
                match_time = match_datetime.strftime('%H:%M')
                
                # 日付ごとに試合情報を保存
                matches_by_date[match_date].append({
                    'time': match_time,
                    'home': home_team,
                    'away': away_team
                })
            
            # スケジュールフォーマット
            message = format_schedule(matches_by_date, today, week_later)
            
            # Discord に投稿
            post_discord(message, user_config['football']['webhook'])
            print('送信完了: プレミアリーグ週間スケジュール')
        else:
            message = "今週のプレミアリーグの試合はありません。"
            post_discord(message, user_config['football']['webhook'])
            print(message)
    except requests.exceptions.RequestException as e:
        error_message = f"APIエラー: {str(e)}"
        print(error_message)
        post_discord(error_message, user_config['football']['webhook'])
