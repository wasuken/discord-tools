import requests
import os
import json

def read_config():
    """
    設定ファイルをよみとる
    現時点では共通のファイル(~/discord/config.json)をよみとるようにしている。
    """
    config_path = "/etc/discord/config.json"
    config_etc_path = "~/discord/config.json"
    config_expand_path = os.path.expanduser(config_path)
    path_list = []
    if os.path.exists(config_expand_path):
        with open(config_expand_path) as f:
            data = json.load(f)
            print(f"Data from {config_path}")
            return data
    elif os.path.exists(config_etc_path):
        with open(config_etc_path) as f:
            data = json.load(f)
            print(f"Data from {config_etc_path}")
            return data
    else:
        print(f"{config_path}: does not exists")
    return None

def post_discord(message: str, webhook_url: str):
    """シンプルに文字列だけdiscordの指定webhook_urlへ送信する関数"""
    data = {"content": message}
    res = requests.post(webhook_url, data=data)
    return res

def remove_lockfile(lock_path):
    """
    ロックファイルをけす
    """
    if os.path.exists(lock_path):
        os.remove(lock_path)

def post_discord_if_not_same(message: str, webhook_url: str, lock_path: str):
    """
    ロックファイルを作成しつつ、おなじ内容は送信しないようにする
    ロックファイルのパスはlock_pathにて定義
    returnはBool値
    """
    # 前回の通知内容を読み込み
    if os.path.exists(lock_path):
        with open(lock_path, "r") as f:
            last_msg = f.read().strip()
            # 同じ内容のメッセージの場合
            if last_msg == message:
                # なにもしない
                return False

    post_discord(message, webhook_url)
    with open(lock_path, "w") as f:
        f.write(message.strip())

    return True

def post_discord_with_file(message: str, webhook_url: str, file_path: str):
    """
    シンプルに文字列と単品ファイルだけdiscordの指定webhook_urlへ送信する関数
    複数ファイル送信は需要があればつくる
    """
    filename = os.path.basename(file_path)
    data = {
        "content": message
    }

    # ファイル部分の設定
    with open(file_path, 'rb') as f:
        file_content = f.read()

    files = {
        "file": (filename, file_content)
    }

    # 送信
    res = requests.post(webhook_url, files=files, data=data)
    return res


# logs
def already_filter(items, logpath):
    """
    開発中
    """
    sha1 = hashlib.sha1()
    f = open(logpath, 'r')
    result = []
    for item in items:
        sha1.update(item.encode("utf-8"))
        if f.readlines() in sha1.hexdigest():
            result.append(item)
            f.close()
    return result

def write_log(items, logpath):
    """
    開発中
    """
    f = open(logpath, 'r')
    result = []
    for item in items:
        sha1.update(item.encode("utf-8"))
        if f.readlines() in sha1.hexdigest():
            result.append(item)
            f.close()
    return result
