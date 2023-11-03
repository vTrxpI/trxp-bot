import discord
import re
import random
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta
from bot import Bot
from discord.ext import tasks

class ReminderCog(commands.Cog):
    """A cog for reminder commadns.
    
    Parameters
    ----------
    bot : commands.Bot
        The bot instance, passed in from setup function..
    """
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: Bot = bot
        self.remindertask.start()
        
        self.responses = [
    "Gotcha! I'll make sure to remind you {time_format} | {message}",
    "Roger that! You'll be reminded {time_format} | {message}",
    "Copy that! Your reminder is scheduled {time_format} | {message}",
    "Consider it done! You'll be reminded {time_format} | {message}",
    "Time warp initiated! Expect a reminder {time_format} | {message}",
    "No problemo! Reminding you {time_format} | {message}",
    "Your wish is my command! Reminder set {time_format} | {message}",
    "All systems go! You'll hear from me {time_format} | {message}",
    "Mission accepted! Expect a reminder {time_format} | {message}",
    "Locked and loaded! I'll remind you {time_format} | {message}",
    "Just like clockwork! Your reminder is scheduled {time_format} | {message}",
    "On it, captain! Expect a nudge from me {time_format} | {message}",
    "Reminding you is my specialty! Look out for it {time_format} | {message}",
    "Time travel engaged! You'll hear from me {time_format} | {message}",
    "Aye aye! Setting a reminder for {time_format} | {message}",
    "Ready, set, remind! Expect my message {time_format} | {message}",
    "Your personal reminder is in the works! {time_format} is the time | {message}",
    "Counting down {time_format} for your reminder | {message}",
    "The reminder train is departing {time_format} | Next stop: {message}",
    "Watch your inbox! A reminder is scheduled {time_format} | {message}"
]
    
        
    def cog_unload(self) -> None:
        self.remindertask.cancel()
        
    def get_reminder_time(self, time: str) -> datetime:
        if 's' in time:
            time = time.strip('s')
            time = datetime.now() + timedelta(seconds=int(time))
        elif 'm' in time:
            time = time.strip('m')
            time = datetime.now() + timedelta(minutes=int(time))
        elif 'h' in time:
            time = time.strip('h')
            time = datetime.now() + timedelta(hours=int(time))
        elif 'd' in time:
            time = time.strip('d')
            time = datetime.now() + timedelta(days=int(time))
        elif 'w' in time:
            time = time.strip('w')
            time = datetime.now() + timedelta(weeks=int(time))
        
        return time

    async def get_reminder_id(self) -> int:
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT id FROM reminders ORDER BY id DESC LIMIT 1')
                data = await cursor.fetchone()
                
                if not data:
                    remID = 1
                else:
                    remID = data[0] + 1
            await conn.commit()
                
        return remID
                    
    @tasks.loop(seconds=10)
    async def remindertask(self) -> None:
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT * FROM reminders')
                data = await cursor.fetchall()
                
                if not data:
                    return
                
                for m in data:
                    date = datetime.fromisoformat(m[2])
                    
                    if date <= datetime.now():
                        user = self.bot.get_user(m[0])
                        
                        if not user:
                            continue
                        
                        date = discord.utils.format_dt(date)
                        
                        embed = discord.Embed(description=f'Howdy, {user.mention}! On {date} you told me to remind you: {m[3]}', color=discord.Color.green())
                        await user.send(embed=embed)
                        
                        await cursor.execute('DELETE FROM reminders WHERE id = ?', (m[1],))
            await conn.commit()
                        
    @remindertask.before_loop
    async def before_remindertask(self) -> None:
        await self.bot.wait_until_ready()
    
    @commands.command(name='remindme', aliases=['remind', 'reminder'])
    @commands.guild_only()
    async def _remindme(self, ctx: Context, time: str, *, reminder: str) -> None:
        """A command to set reminders.
        
        Parameters
        ----------
        ctx : discord.ext.commands.Context
            The context of the command.
        time : str
            The time to wait before sending the reminder.
        reminder : str
            The reminder message.
        """
        
        await ctx.message.delete()
        
        if not re.match(r"^\d+[smwd]$", time):
            embed = discord.Embed(description='Invalid time format. Please use the following format: `1s` (1 second), `1m` (1 minute), `1h` (1 hour), `1d` (1 day), `1w` (1 week).', color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        dTime = self.get_reminder_time(time)
        remID = await self.get_reminder_id()
        
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('INSERT INTO reminders (user, id, time, message) VALUES (?, ?, ?, ?)', (ctx.author.id, remID, dTime, reminder))
        
        dTime = discord.utils.format_dt(dTime, style='R')

        response = random.choice(self.responses)
        
        embed = discord.Embed(description=response.format(time_format=dTime, message=reminder), color=discord.Color.green())
        
        await ctx.send(embed=embed)

async def setup(bot: Bot) -> None:
    await bot.add_cog(ReminderCog(bot))