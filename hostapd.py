import subprocess
import json
import requests
import time
from datetime import datetime
import re
from common import post_discord_if_not_same, read_config

def get_hostapd_info():
    try:
        # ステータス取得
        status = subprocess.check_output(["sudo", "hostapd_cli", "status"], text=True)

        # 接続クライアント取得
        clients = subprocess.check_output(["sudo", "hostapd_cli", "all_sta"], text=True)

        return status, clients
    except subprocess.CalledProcessError as e:
        return f"Error getting hostapd info: {str(e)}", ""

def parse_clients(clients_str):
    mac_addresses = clients_str.strip().split('\n')
    client_details = []

    for mac in mac_addresses:
        if mac:  # Skip empty lines
            try:
                # 各クライアントの詳細情報を取得
                details = subprocess.check_output(["sudo", "hostapd_cli", "sta", mac], text=True)
                client_details.append(details)
            except subprocess.CalledProcessError:
                continue

    return client_details

def send_to_discord(status, clients, webhook_url):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # メッセージの作成
    message = f"**WiFi AP Status Update** ({current_time})\n"
    message += "```\n"  # Discord's code block formatting

    # ステータス情報の追加
    message += "=== Status ===\n"
    message += status + "\n"

    # 接続クライアント情報の追加
    message += "\n=== Connected Clients ===\n"
    client_details = parse_clients(clients)
    for client in client_details:
        message += client + "\n"

    message += "```"  # Close code block

    # Discordの文字数制限（2000文字）を考慮
    if len(message) > 1900:
        message = message[:1900] + "```\n... (truncated)"

    # Webhook送信
    payload = {
        "content": message
    }

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {str(e)}")

def main():
    config = read_config()
    webhook_url = config['hostapd']['webhook']
    print("Starting Hostapd Discord Monitor...")
    status, clients = get_hostapd_info()
    send_to_discord(status, clients, webhook_url)

if __name__ == "__main__":
    main()
