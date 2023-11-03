import discord
import asyncio
from os import getenv
from dotenv import load_dotenv; load_dotenv()
from bot import Bot

discord.utils.setup_logging()

async def main() -> None:
    async with Bot() as bot:
        for ext in bot.coglist:
            await bot.load_extension(ext)
            
        await bot.start(getenv('TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())