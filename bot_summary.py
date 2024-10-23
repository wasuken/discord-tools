from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

import discord
from discord.ext import commands
import random
from common import post_discord, read_config

SUMMARIZER = LsaSummarizer()

CONFIG = read_config()

TOKEN = CONFIG['summary_bot']['token']
TXT_DIR = CONFIG['summary_bot'].get('directory', '/etc/discord/txt/')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    case_insensitive=True,
    intents=intents
)


# 文章の要約
def text_summarize(text):
    rst = []
    parser = PlaintextParser.from_string(text, Tokenizer("japanese"))
    summary = SUMMARIZER(parser.document, 5)

    for sentence in summary:
        rst.append(sentence)

    return '\n'.join(rst)

@bot.event
async def on_message(message: discord.Message):
    # ボット自身のメッセージは無視
    if message.author.bot:
        return

    # 指定したチャンネル以外では返信しない
    if str(message.channel.id) not in CONFIG['summary_bot']['target_channel_id_list']:
        return
