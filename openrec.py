import requests
import json
from common import post_discord_if_not_same, read_config

class LiveInfo(object):
    title = ''
    channel_id = ''
    nickanme = ''

    def __init__(self, title, channel_id, nickname):
        self.title = title
        self.channel_id = channel_id
        self.nickname = nickname

    def to_content(self):
        return f"{self.title}:{self.nickname}({self.channel_id})"

"""
urlにrequest(GET)して、整形した結果をLiveInfoリストで返却する
"""
def liveinfo_list_from_api(url):
    res = requests.get(url)
    data = res.json()
    rst = []
    for live in data:
        title = live['title']
        channel_id = live['channel']['id']
        nickname = live['channel']['nickname']
        rst.append(LiveInfo(title=title, channel_id=channel_id, nickname=nickname))

    return rst

if __name__ == "__main__":
    rec_config = read_config()
    webhook_url = rec_config["openrec"]["webhook"]
    api_endpoint_url = rec_config["openrec"]["api_endpoint"]
    id_list = rec_config["openrec"]["channel_id_list"]
    list = liveinfo_list_from_api(api_endpoint_url)
    info_list = []
    for info in list:
        print(info.channel_id)
        for id in id_list:
            if info.channel_id in id:
                info_list.append(info)


    content = '\n'.join([x.to_content() for x in info_list])
    if len(content) <= 0:
        print("Not send to discord because content is empty.")
        exit()
    post_discord_if_not_same("openrec監視：" + '\n' +  content, webhook_url)
