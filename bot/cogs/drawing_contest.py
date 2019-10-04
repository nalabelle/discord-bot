from datetime import datetime, timedelta
import queue
import discord
from discord.ext import tasks,commands
from services.contest import ContestTracking
import services.config
from ext import custom_permissions

class DrawingContest(commands.Cog):
    """
    Drawing Contest Commands

    - Runs a drawing contest and collects entries
    - Uses a per-guild prompt list
    - Allows one contest series per guild (expects to monitor one channel)
    """

    def __init__(self, bot):
        self.bot = bot
        self.execution_queue = []
        self.draw_guilds = dict()
        config = services.config.get('drawing_contest')
        if config:
            for guild_id, entry in config.items():
                ct = ContestTracking.deserialize(entry["tracking"])
                self.draw_guilds[guild_id]["channel_id"] = entry["channel_id"]
                self.draw_guilds[guild_id]["tracking"] = ct
                current_contest = ct.current_contest
                if current_contest is not None:
                    contest_end = ct.get_contest_end()
                    self.execution_queue.append((contest_end, guild_id))
            self.execution_queue.sort(key=lambda tup: tup[0])

    def save_draw_guilds(self):
        services.config.set('drawing_contest', self.draw_guilds)
        services.config.save()

    @commands.Cog.listener()
    async def on_ready(self):
        """Load the timers for each contest series"""
        self.prompt_timer.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.message_is_drawing_maybe(message):
            draw_guild = self.get_draw_guild(message.guild)
            draw_guild.add_entry(message.id)
            await message.add_reaction('👍')
            self.save_draw_guilds()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        if self.message_is_drawing_maybe(message):
            draw_guild = self.get_draw_guild(message.guild)
            entry = draw_guild.get_entry(message.id)
            if entry is None:
                return
            emoji = reaction.emoji
            if emoji is None:
                return
            if hasattr(emoji, 'name'):
                name = emoji.name
                if name == 'thumbsdown':
                    entry.removed = True
                    self.save_draw_guilds()

    def message_is_drawing_maybe(self, message):
        # we're looking for user messages with attachments in our guild
        # drawing channel...
        if message.type != discord.MessageType.default:
            return False
        if len(message.attachments) < 1:
            return False
        if message.guild is None:
            return False
        if str(message.guild.id) in self.draw_guilds:
            channel_id = self.draw_guilds[str(message.guild.id)]["channel_id"]
            if str(message.channel.id) == channel_id:
                return True

    def cog_unload(self):
        self.prompt_timer.cancel()

    @tasks.loop(seconds=60)
    async def prompt_timer(self):
        now = datetime.now()
        for contest_end, guild_id in self.execution_queue:
            if now > contest_end:
                await self.end_contest(guild_id)
                await self.start_contest(guild_id)
            else:
                break

    def get_draw_guild(self, guild: discord.Guild):
        if str(guild.id) in self.draw_guilds:
            draw_guild = self.draw_guilds[str(guild.id)]
        else:
            draw_guild = ContestTracking()
            self.draw_guilds[str(guild.id)] = draw_guild
        return draw_guild

    async def end_contest(self, guild: discord.Guild):
        draw_guild = self.get_draw_guild(guild)
        channel_id = self.draw_guilds[str(guild.id)]["channel_id"]
        channel = self.bot.get_channel(channel_id)
        async with channel.typing():
            if draw_guild.stop_contest():
                self.save_draw_guilds()
                await channel.send('Drawing Contest has ended :(')
            else:
                await channel.send('I couldn\'t find a contest to end')

    async def start_contest(self, guild: discord.Guild, interval_days: int=None):
        draw_guild = self.get_draw_guild(guild)
        channel_id = self.draw_guilds[str(guild.id)]["channel_id"]
        channel = self.bot.get_channel(channel_id)
        draw_guild.start_contest(interval_days)
        async with channel.typing():
            prompt = draw_guild.get_current_prompt()
            await self.say_prompt(channel, prompt)
            contest_end = draw_guild.get_contest_end()
            if contest_end is not None:
                self.save_draw_guilds()
                self.execution_queue.append((contest_end, guild.id))
                await channel.send('Contest ends at {}'.format(contest_end))

    async def say_prompt(self, channel: discord.abc.Messageable, prompt: str=None):
        if prompt is None:
            await channel.send('I\'m all out of drawing prompts!')
        else:
            await channel.send('Draw: **{}**!'.format(prompt))

    @commands.group(name="draw")
    async def draw(self, ctx):
        """Drawing Contest Commands"""

    @draw.group(name="contest", description="Drawing Contest functions")
    async def contest(self, ctx):
        """Drawing Contest Functions"""

    @contest.command(description="Start the contest!")
    @commands.guild_only()
    @commands.has_permissions(manage_webhooks=True)
    async def start(self, ctx, interval_days: int):
        """Sets the drawing contest timer for the specified amount of days"""
        draw_guild = self.get_draw_guild(ctx.guild)
        self.draw_guilds[str(ctx.guild.id)]["channel_id"] = ctx.channel.id
        await self.start_contest(ctx.guild, interval_days)

    @contest.command(description="Stop the contest :(")
    @commands.guild_only()
    @commands.has_permissions(manage_webhooks=True)
    async def stop(self, ctx):
        """Ends the current drawing contest and unsets the next execution"""
        await self.end_contest(ctx.guild)

    @draw.group(
            name="prompt",
            invoke_without_command=True,
            description="Get a drawing prompt"
            )
    @commands.guild_only()
    async def prompt(self, ctx):
        """Get a drawing prompt"""
        async with ctx.typing():
            draw_guild = self.get_draw_guild(ctx.guild)
            prompt = draw_guild.get_current_prompt()
            self.save_draw_guilds()
            await self.say_prompt(ctx, prompt)

    @prompt.command(description='Add a drawing subject')
    @commands.guild_only()
    async def add(self, ctx, *, phrase : str):
        """Adds a drawing subject to guild prompts"""
        async with ctx.typing():
            draw_guild = self.get_draw_guild(ctx.guild)
            if draw_guild.add_prompt(phrase):
                self.save_draw_guilds()
                await ctx.send('added "{}" to drawing prompts!'.format(phrase))
            else:
                await ctx.send('sorry, I didn\'t understand that one.')

    @prompt.command(description='Remove a drawing subject')
    @commands.guild_only()
    @commands.has_permissions(manage_webhooks=True)
    async def remove(self, ctx, *, phrase : str):
        """Removes a drawing subect from guild prompts"""
        async with ctx.typing():
            draw_guild = self.get_draw_guild(ctx.guild)
            if draw_guild.remove_prompt(phrase):
                self.save_draw_guilds()
                await ctx.send('removed "{}" from drawing prompts!'.format(phrase))
            else:
                await ctx.send('sorry, I didn\'t understand that one.')

    @prompt.command(description='Shuffle drawing subjects',hidden=True)
    @commands.guild_only()
    @commands.has_permissions(manage_webhooks=True)
    async def shuffle(self, ctx):
        """Shuffles guild prompts"""
        async with ctx.typing():
            draw_guild = self.get_draw_guild(ctx.guild)
            draw_guild.shuffle_prompts()
            self.save_draw_guilds()
            await channel.send('Done!')

