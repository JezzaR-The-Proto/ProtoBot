import discord, time, sys, psutil, configparser, os
from discord.ext import commands
from humanfriendly import format_timespan
from CheckDisabled import CheckDisabled
from CheckBlacklist import CheckBlacklist

class Info(commands.Cog):
	def __init__(self, bot):
		self.StartTime = time.time()
		self.Config = configparser.ConfigParser()
		self.Config.read(f".{os.path.sep}Config{os.path.sep}config.ini")
		self.bot = bot

	@commands.command(help="Displays the bot's uptime")
	async def uptime(self, ctx):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "uptime"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		self.Uptime = format_timespan(time.time() - self.StartTime, max_units=3)
		await ctx.send(f"ProtoBot has been up for {self.Uptime}")

	@commands.command(brief="Displays a user's stats", help="Displays a user's stats.\nDefaults to the author if there is no mention.")
	async def info(self, ctx, *user: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "info"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		InfoMsg = await ctx.send("<a:loading:725022752150519941> | Getting user info")
		if user == ():
			user = ctx.author
		else:
			user = user[0]
		StatsEmbed = discord.Embed(title=f"{user}'s info",description=f"**User ID:** {user.id}")
		StatsEmbed.set_thumbnail(url=user.avatar_url)
		StatsEmbed.add_field(name="**Server nick**", value=user.nick, inline = False)
		Weekdays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
		Weekday = Weekdays[int(user.joined_at.strftime("%w"))]
		StatsEmbed.add_field(name="**Server join time**", value=f"{Weekday}, {user.joined_at.strftime('%B %d')}th {user.joined_at.strftime('%Y')} at {user.joined_at.strftime('%H:%M:%S')}", inline = False)
		Weekday = Weekdays[int(user.created_at.strftime("%w"))]
		StatsEmbed.add_field(name="**User create time**", value=f"{Weekday}, {user.created_at.strftime('%B %d')}th {user.created_at.strftime('%Y')} at {user.created_at.strftime('%H:%M:%S')}", inline = False)
		Roles = []
		for Role in user.roles:
			if "@everyone" not in Role.name:
				Roles.append(Role.name)
		RolesStr = ", ".join(Roles)
		if RolesStr == "":
			RolesStr = "None"
		StatsEmbed.add_field(name=f"**Roles [{len(user.roles) - 1}]**", value=RolesStr)
		StatsEmbed.add_field(name="**Top role**", value=user.top_role)
		await InfoMsg.edit(content="",embed=StatsEmbed)

	@commands.command(help="Displays the current server's stats")
	async def serverinfo(self, ctx):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "serverinfo"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		InfoMsg = await ctx.send("<a:loading:725022752150519941> | Getting server info")
		ServerEmbed = discord.Embed(title=f"Server stats for {ctx.guild.name}",description=f"Server ID: `{ctx.guild.id}`")
		ServerEmbed.set_thumbnail(url=ctx.guild.icon_url)
		ServerEmbed.add_field(name="**Server owner**", value=ctx.guild.owner)
		if ctx.guild.system_channel == None:
			ServerEmbed.add_field(name="**System channel**", value="None")
		else:
			ServerEmbed.add_field(name="**System channel**", value=ctx.guild.system_channel.name)
		ServerEmbed.add_field(name="**Text channels**", value=len(ctx.guild.text_channels))
		ServerEmbed.add_field(name="**Voice channels**", value=len(ctx.guild.voice_channels))
		Users = 0
		Bots = 0
		for Member in ctx.guild.members:
			if Member.bot:
				Bots += 1
			else:
				Users += 1
		ServerEmbed.add_field(name="**Total members**", value=f"{len(ctx.guild.members)} - {Users} users, {Bots} bots")
		await InfoMsg.edit(content="",embed=ServerEmbed)

	@commands.command(help="Displays the bot's ping")
	async def ping(self, ctx):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "ping"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		await ctx.send(f"Current ping: {round(self.bot.latency*1000)}ms")

	@commands.command(help="Displays bot info")
	async def botinfo(self, ctx):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "botinfo"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		InfoMsg = await ctx.send("<a:loading:725022752150519941> | Getting bot info")
		BotEmbed = discord.Embed(title="ProtoBot information", description="Help command: p+help")
		BotEmbed.set_thumbnail(url=self.bot.user.avatar_url)
		BotEmbed.add_field(name="Python information:", value=f"```OS: {sys.platform}\nPython version: {sys.version}\nDiscord.py version: {discord.__version__}\nPsutil version: {psutil.__version__}```", inline=False)
		self.Uptime = format_timespan(time.time() - self.StartTime, max_units=3)
		BotEmbed.add_field(name="Bot information:", value=f">>> Uptime: {self.Uptime}\nServers: {len(self.bot.guilds)}\nUsers: {len(self.bot.users)}\nPing: {round(self.bot.latency*1000)}ms")
		NetSend = psutil.net_io_counters().bytes_sent
		Units = ["bytes","KB","MB","GB","TB"]
		SendUnit = 0
		while NetSend > 1024:
			NetSend = NetSend / 1024
			SendUnit += 1
		NetRecv = psutil.net_io_counters().bytes_recv
		RecvUnit = 0
		while NetRecv > 1024:
			NetRecv = NetRecv / 1024
			RecvUnit += 1
		BotEmbed.add_field(name="Process information:", value=f">>> CPU Usage: {psutil.cpu_percent()}%\nRAM Usage: {psutil.virtual_memory().percent}%\nNetwork send: {round(NetSend, 2)}{Units[SendUnit]}\nNetwork recv: {round(NetRecv, 2)}{Units[RecvUnit]}")
		await InfoMsg.edit(content="", embed=BotEmbed)

	@commands.command(help="View the changelog")
	async def changelog(self, ctx):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "changelog"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		Log = []
		ChangelogMsg = await ctx.send("<a:loading:725022752150519941> | Opening changelog...")
		with open(f".{os.path.sep}Config{os.path.sep}changelog.txt") as Changelog:
			Line = Changelog.readline()
			while Line:
				Log.append(Line)
				Line = Changelog.readline()
		self.Config = configparser.ConfigParser()
		self.Config.read(f".{os.path.sep}Config{os.path.sep}config.ini")
		ChangelogEmbed = discord.Embed(title="ProtoBot changelog", description=f"Current version: {self.Config['Settings']['Version']}")
		while len(Log) > 24:
			del Log[0]
		for Line in Log:
			ChangelogEmbed.add_field(name=f"Version: {Line.split(':')[0]}", value=f"{Line.split(':')[-1][1:]}")
		await ChangelogMsg.edit(content="", embed=ChangelogEmbed)

	@commands.command(help="Get a user's avatar")
	async def avatar(self, ctx, *User: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "avatar"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if User == ():
			User = ctx.author
		else:
			User = User[0]
		await ctx.send(f"{User.mention}'s avatar: {User.avatar_url}")

	@commands.command(help="Get a link to the support server")
	async def support(self, ctx):
		await ctx.send("The support server is being setup. Try again later.")

def setup(bot):
	bot.add_cog(Info(bot))
