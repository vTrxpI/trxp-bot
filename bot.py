import discord
import asqlite
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(command_prefix='?', intents=intents)
        
        self.coglist = [
            'jishaku',
            'cogs.reminder',
        ]
    
    async def on_ready(self) -> None:
        print(f'Logged in as {self.user} ({self.user.id})')
        
    async def setup_hook(self) -> None:
        async with asqlite.connect('main.db') as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('CREATE TABLE IF NOT EXISTS reminders (user INTEGER, id INTEGER, time TEXT, message TEXT)')
                
        self.pool = await asqlite.create_pool('main.db')
        
    
    async def close(self) -> None:
        await self.pool.close()
        await super().close()