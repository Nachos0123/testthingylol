from discord.ext.commands import *
from medbot.managers.bot import Bot

class Sync(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    @has_permissions(administrator=True)
    async def sync(self, ctx):
        synced = await self.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)}")

async def setup(bot: Bot):
    await bot.add_cog(Sync(bot))