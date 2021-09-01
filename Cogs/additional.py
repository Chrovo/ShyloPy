import datetime
import random
import re
import time
import zlib
from io import BytesIO

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import BucketType


class additional(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._cache = {} # cache rtfm command results

    @commands.command()
    async def ping(self, ctx):
        before = time.monotonic()

        message = await ctx.send('Pinging...')

        ping = (time.monotonic() - before) * 1000

        if ping < 200:
            color = 0x35fc03
        elif ping < 350:
            color = 0xe3f51d
        elif ping < 500:
            color = 0xf7700f
        else:
            color = 0xf7220f

        pEmbed = discord.Embed(title="Stats.", color=color)
        pEmbed.add_field(name="Latency", value=f'{int(ping)}ms')
        pEmbed.add_field(name="API", value=f'{round(self.bot.latency * 1000)}ms')
        pEmbed.set_thumbnail(url=self.bot.user.avatar_url)

        await message.edit(content=None, embed=pEmbed)
    
    @commands.command(aliases=['docs', 'documentation', 'rtfd'])
    @commands.cooldown(1, 5, BucketType.user)
    async def rtfm(self, ctx, lib: str, search: str):
        results = self._cache.get(lib+"/"+search.lower()) # get the stored results
        
        if not results:
            ALL_LIBS = {
                'python':'https://docs.python.org/3/objects.inv',
                'dpy':'https://discordpy.readthedocs.io/en/latest/objects.inv',
                'dpy-master':'https://discordpy.readthedocs.io/en/master/objects.inv'
                'requests':'https://docs.python-requests.org/en/latest/objects.inv',
                'pygame':'https://www.pygame.org/docs/objects.inv',
                'lark':'https://lark-parser.readthedocs.io/en/latest/objects.inv',
                'aiohttp':'https://docs.aiohttp.org/en/stable/objects.inv',
                'numpy':'https://numpy.org/doc/1.20/objects.inv',
                'matplotlib':'https://matplotlib.org/stable/objects.inv',
                'pandas':'https://pandas.pydata.org/pandas-docs/stable/objects.inv',
                'asyncpg':'https://magicstack.github.io/asyncpg/current/objects.inv',
                'pillow':'https://pillow.readthedocs.io/en/stable/objects.inv',
            }

            try:
                library = ALL_LIBS[lib.lower()]
            except KeyError:
                return await ctx.send(
                    f'That library is not supported yet! Try these instead\n{", ".join(ALL_LIBS.keys())}'
                )
        
            embed = discord.Embed(title=f"Documentation search!", description="")
            search = re.escape(search)

            async with self.bot.session.get(library) as r:
                data = BytesIO(await r.read())
                decobj = zlib.decompressobj()

                for i in range(4):
                    data.readline()

                info = data.read()
                decompressed = str(decobj.decompress(info)).split('\\n')
                sug = [line for line in decompressed if re.search(search, line)]

                if not sug:
                    return await ctx.send("Could not find anything.")
                    
                num_sug = len(sug) if len(sug) < 10 else 10
                
                for j in range(num_sug):
                    embed.description+=f"[`{sug[j].split()[0]}`]({library[:-11]}{sug[j].split()[-2][:-1]}{sug[j].split()[0]})\n"

                self._cache[lib+"/"+search.lower()] = embed # store the results

                return await ctx.send(embed=embed)

        return await ctx.send(embed=results)
    
    @rtfm.error
    async def rtfm_error(self, ctx, error):
        embed = discord.Embed(title="An error has occurred", description="", colour=discord.Colour.red())

        if isinstance(error, commands.MissingRequiredArgument):
            embed.description+=f"You did not use the command properly\n**Usage:** shylo!{ctx.command.qualified_name} {ctx.command.signature}"
            
        elif isinstance(error, commands.CommandOnCooldown):
            embed.description+=f"You are on cooldown! Please wait {round(error.retry_after)}"
            
        return await ctx.send(embed=embed)
            
# ^ Documentation search command

## *more python switch cases*

    @commands.command(aliases=['announce'])
    async def a(self, ctx, channel: discord.TextChannel, *, msg: str):
        if ctx.author.guild_permissions.administrator:
            await ctx.send('Gotcha.')
            channel = self.bot.get_channel(857679429128159242)
            await channel.send(msg)
 
## ^ Announce command lol

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            if after.nick.startswith('!'):
                nick = [char for char in after.nick if char != '!']
                await after.edit(nick="".join(nick))

## ^ Anti-hoisting

def setup(bot):
    bot.add_cog(additional(bot))
