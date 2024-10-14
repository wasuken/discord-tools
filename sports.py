import requests
from datetime import datetime, timezone, timedelta
from common import post_discord, read_config

# Premier League competition ID
PREMIER_LEAGUE_ID = 2021

# UTCからJSTに変換する関数
def convert_to_jst(utc_time_str):
    # まずUTCタイムをパース
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")

    # タイムゾーンをUTCに設定
    utc_time = utc_time.replace(tzinfo=timezone.utc)

    # JSTはUTC+9時間
    jst_time = utc_time + timedelta(hours=9)

    # フォーマットを日本の標準的な表示形式に変換
    return jst_time.strftime('%Y-%m-%d %H:%M')

if __name__ == '__main__':
    user_config = read_config()
    today = datetime.today()
    week_later = today + timedelta(days=7)

    date_from = today.strftime('%Y-%m-%d')
    date_to = week_later.strftime('%Y-%m-%d')

    # API request URL for today's matches
    url = f"https://api.football-data.org/v4/competitions/{PREMIER_LEAGUE_ID}/matches"

    # Set up the headers including the API key
    headers = {
        'X-Auth-Token': user_config['football']['api_key']
    }

    # Make the request
    response = requests.get(url, headers=headers, params={'dateFrom': date_from, 'dateTo': date_to})

    # Parse and print match data
    if response.status_code == 200:
        matches = response.json().get('matches', [])
        msgs = []
        if matches:
            for match in matches:
                home_team = match['homeTeam']['name']
                away_team = match['awayTeam']['name']
                match_time = convert_to_jst(match['utcDate'])
                msgs.append(f"{home_team} vs {away_team} at {match_time}")
        else:
            print("No matches found for today.")
        content = '\n'.join(msgs)
        post_discord("今週のサッカー：" + '\n' +  content, user_config['football']['webhook'])
        print('send.')
    else:
        print(f"Error: {response.status_code}")
