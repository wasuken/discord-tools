import feedparser
from common import post_discord, read_config


def parse_rss(url: str, limit = 5) -> str:
    rss = feedparser.parse(url)
    output = []
    for content in rss['entries'][0:limit]:
        output.append('Title: {}\n \tLink: {}\n'.format(content['title'], content['link']))

    return output

if __name__ == "__main__":
    user_config = read_config()
    webhook_url = user_config["news"]["webhook"]
    # 暫定ひとつだけ
    news_url = user_config["news"]["urls"][0]

    content = '\n'.join(parse_rss(news_url))
    post_discord("テクノロジニュース：" + '\n' +  content, webhook_url)
    # print(content)
