import disnake
import os
import asyncio
from config import settings
from disnake.ext import commands
from cogs.utils.Data import DataBase
import logging

logger = logging.getLogger(__name__)
intents = disnake.Intents.all()
activity = disnake.Activity(
    name="Flonium",
    type=disnake.ActivityType.playing,
    details="Приватный сервер Minecraft"
)
bot = commands.Bot(command_prefix=settings['prefix'], intents=intents,
                   test_guilds=[1184123739764428880], activity=activity)
bot.remove_command('help')
data = DataBase()


@bot.event
async def on_ready():
    print("Бот успешно запущен")


for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        if not file.startswith('__init__'):
            bot.load_extension(f"cogs.{file[:-3]}")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")
    await data.create_table()


if __name__ == '__main__':
    asyncio.run(main())
    bot.run(settings['token'])
