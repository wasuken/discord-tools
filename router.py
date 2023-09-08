import json
from urllib.request import Request, urlopen
from common import post_discord, read_config

if __name__ == "__main__":
    user_config = read_config()
    webhook_url = user_config["router"]["webhook"]
    lines = []
    with open('/var/lib/misc/dnsmasq.leases', 'r') as f:
        lines = [x for x in [y.split(' ')[3] for y in f.readlines()] if len(x) > 2]

    linesStr = '\n'.join(lines)
    post_discord("現在IPを貸してる端末一覧：" + '\n' +  linesStr, webhook_url)
