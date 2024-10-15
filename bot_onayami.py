import discord
from discord.ext import commands
import random
from common import post_discord, read_config

CONFIG = read_config()

TOKEN = CONFIG['nayami_bot']['token']
TXT_DIR = CONFIG['nayami_bot'].get('directory', '/etc/discord/txt/')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    case_insensitive=True,
    intents=intents
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


def choice_random_quote(file_name):
    with open(f'{TXT_DIR}{file_name}') as f:
        quotes_list = f.readlines()
    return random.choice(quotes_list)

async def send_random_quote(ctx, file_name):
    response = choice_random_quote(file_name)
    await ctx.send(f'{response}')

@bot.event
async def on_message(message: discord.Message):
    # ボット自身のメッセージは無視
    if message.author.bot:
        return

    # 指定したチャンネル以外では返信しない
    if str(message.channel.id) not in CONFIG['nayami_bot']['target_channel_id_list']:
        return

    # 10回に1回ランダムに返信
    if random.randint(1, 10) == 1:
        file_names = CONFIG['nayami_bot']['quotes']
        file_name = random.choice(file_names) + '.txt'
        response = choice_random_quote(file_name)
        await message.channel.send(response)

    # 他のコマンドも動くようにする
    await bot.process_commands(message)

@bot.command(name="kaiwa", descricption="会話できるよ")
async def kaiwa(ctx, arg=None):
    # 設定ファイル内のquotes配列と一致するか確認
    if arg in CONFIG['nayami_bot']['quotes']:
        await send_random_quote(ctx, arg + '.txt')
    else:
        await ctx.send(f'指定されたカテゴリが見つかりません: {arg}')

bot.run(TOKEN)
