from discord.ext import commands

import config
from cog_helpers import utility_helper
from cog_helpers.general_helper import get_info_embd

class Utility(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f"Bot Latency (aka Ping) is : `{round(self.bot.latency * 1000, 2)}`ms")

    @commands.guild_only()
    @commands.command()
    async def roll(self, ctx, max_value : int = 100):
        reply = await utility_helper.roll(max_value, ctx.author)
        await ctx.send(reply)

    @roll.error
    async def roll_handler(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.reply(f"Gib a interger as an argument like `{ctx.prefix}roll 69`")
        else:
            await ctx.reply(error)

    @commands.command(name="support_server", aliases=["ss"])
    async def support_server(self, ctx):
        reply = await utility_helper.get_support_server_embed()
        await ctx.send(embed=reply)

    @commands.command(name="about")
    async def about(self, ctx):
        reply = await utility_helper.get_about_embed()
        await ctx.send(embed=reply)

    @commands.command(name="vote")
    async def vote(self, ctx):
        reply = await utility_helper.get_vote_embed()
        await ctx.send(embed=reply)

    @commands.command(name="invite", aliases=["inv"])
    async def invite(self, ctx):
        reply = await utility_helper.get_invite_embed()
        await ctx.send(embed=reply)

    @commands.cooldown(1, 60 * 60, type=commands.BucketType.user)
    @commands.command(name="suggest")
    async def suggest(self, ctx, *message):
        await utility_helper.register_suggestion(ctx, message)
        await ctx.send("Thanks a lot for suggesting something, your suggestion is sent to devs :]")

    @suggest.error
    async def suggest_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            reply = await get_info_embd(title="Breh, whats this?", desc="You must provide a suggestion too :/", footer="You can only suggest once an hour, Like this ``````", color=config.ERROR_COLOR)
            await ctx.reply(embed=reply)
        else:
            await ctx.reply(error)
            
def setup(bot):
    bot.add_cog(Utility(bot))