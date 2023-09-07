import json
import requests
from datetime import datetime
import numpy as np
import calendar
import os
import matplotlib.patches as patches
import matplotlib.pyplot as plt

from common import post_discord_with_file, read_config

def generate_calendar_image(dates, image_path):
    # 日付配列から年と月を取得（最初の日付を基にする）
    year = dates[0].year
    month = dates[0].month

    # カレンダーを取得
    first_day, last_day = calendar.monthrange(year, month)
    calendar_array = np.zeros((6, 7))  # 最大6週、7日（6x7マトリックス）

    # カレンダー配列に日付をセット
    day = 1
    for i in range(6):
        for j in range(7):
            if (i == 0 and j < first_day) or (day > last_day):
                calendar_array[i, j] = 0
            else:
                calendar_array[i, j] = day
                day += 1

    # 画像生成
    fig, ax = plt.subplots(figsize=(7, 6))

    # 背景を透明にする
    background = np.ones((6, 7, 4))
    background[..., :3] = 1  # 白色
    background[..., 3] = 0  # 完全に透明
    plt.imshow(background, extent=[0, 7, 0, 6], origin='upper')

    # タイトルと軸を設定
    plt.title(f"{year}/{month}", fontsize=14)
    plt.axis('off')

    # 日付配列に基づいて色をつける
    highlighted_days = [date.day for date in dates if date.year == year and date.month == month]
    for i in range(6):
        for j in range(7):
            day = calendar_array[i, j]

            # パネルの色を設定
            panel_color = 'lightgreen' if day in highlighted_days else 'white'
            rect = patches.Rectangle((j, 5 - i), 1, 1, linewidth=0, edgecolor='none', facecolor=panel_color)
            ax.add_patch(rect)

            # 日付のテキストを描画
            if day != 0:
                plt.text(j + 0.5, 5.5 - i, int(day), ha='center', va='center', fontsize=12, color='black')

    # 画像として保存
    plt.savefig(image_path)


def get_push_events(username):
    url = f"https://api.github.com/users/{username}/events"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Error: {response.status_code}"

    events = response.json()
    push_events = [event for event in events if event['type'] == 'PushEvent']
    return push_events

if __name__ == "__main__":
    user_config = read_config()
    username = user_config["github"]["username"]
    webhook_url = user_config["github"]["webhook"]

    res = get_push_events(username)
    lines = []
    dates = []
    for log in res:
        dt = datetime.strptime(log['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        dates.append(dt)

    image_path = './calendar.png'
    generate_calendar_image(dates, image_path)

    post_discord_with_file("github activity", webhook_url, image_path)
    print('success')
