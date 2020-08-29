#!/usr/bin/python3

import discord, logging, traceback, os, datetime, time, sys, configparser, sqlite3, typing
from discord.ext import commands, tasks
from itertools import cycle

Config = configparser.ConfigParser()
Config.read(f".{os.path.sep}Config{os.path.sep}config.ini")
Prefix = []
Prefix.append(Config["Settings"]["Prefix"])
SettingsDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}ServerSettings.db")
SettingsCursor = SettingsDB.cursor()
BlacklistDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}Blacklist.db")
BlacklistCursor = BlacklistDB.cursor()

async def GetServerPrefix(bot, message):
	global Prefix
	Guild = message.guild
	UserID = bot.user.id
	Prefix.append(f'<@!{UserID}> ')
	Prefix.append(f'<@{UserID}> ')
	if Guild:
		GuildID = Guild.id
		SettingsCursor.execute("SELECT prefix FROM prefix WHERE GuildID = ?",(GuildID,))
		ServerPrefix = SettingsCursor.fetchone()
		if ServerPrefix != None:
			Prefix.append(ServerPrefix[0])
	return Prefix

BasicActivity = discord.Activity(name="for commands", type=discord.ActivityType.watching)
Client = commands.AutoShardedBot(command_prefix = GetServerPrefix, activity = BasicActivity)
Client.remove_command("help")
Count = -1
IgnoreImport = ["Bptf", "Pbl"]

for Extension in [f.replace('.py', '') for f in os.listdir("Cogs") if os.path.isfile(os.path.join("Cogs", f))]:
	if Extension in IgnoreImport:
		continue
	try:
		print(f"Loading extension {Extension}")
		Client.load_extension(f"Cogs.{Extension}")
		print(f"Extension {Extension} loaded.")
	except (discord.ClientException, ModuleNotFoundError, commands.errors.ExtensionFailed):
		print(f'Failed to load extension {Extension}.')
		traceback.print_exc()

@tasks.loop(seconds=30)
async def ChangePresence():
	global Count
	Servers = len(Client.guilds)
	Users = len(Client.users)
	Count += 1
	if Count >= 3:
		Count = 0
	Latency = Client.latency * 1000
	if Latency < 250:
		Lag = discord.Status.online
	elif Latency < 500:
		Lag = discord.Status.idle
	else:
		Lag = discord.Status.dnd
	Status = [discord.Activity(name="for commands", type=discord.ActivityType.watching),
	discord.Activity(name=f"over {Servers} servers", type=discord.ActivityType.watching),
	discord.Activity(name=f"over {Users} users", type=discord.ActivityType.watching)]
	await Client.change_presence(
		activity=Status[Count],
		status=Lag
		)

@Client.command(hidden=True)
@commands.is_owner()
async def load(ctx, cog: str):
	cog = cog.capitalize()
	try:
		LoadingMsg = await ctx.send(f"Loading extension `{cog}`")
		Client.load_extension(f"Cogs.{cog}")
		await LoadingMsg.edit(content=f"Extension `{cog}` loaded.")
		print(f"Extension {cog} loaded")
	except (discord.ClientException, ModuleNotFoundError, commands.errors.ExtensionNotFound):
		await LoadingMsg.edit(content=f"<:error:724683693104562297> | Failed to load extension `{cog}`.")

@Client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, cog: str):
	cog = cog.capitalize()
	try:
		UnloadingMsg = await ctx.send(f"Unloading extension `{cog}`")
		Client.unload_extension(f"Cogs.{cog}")
		await UnloadingMsg.edit(content=f"Extension `{cog}` unloaded.")
		print(f"Extension {cog} unloaded")
	except (discord.ClientException, ModuleNotFoundError):
		await UnloadingMsg.edit(content=f"<:error:724683693104562297> | Failed to unload extension `{cog}`.")
	except commands.errors.ExtensionNotLoaded:
		await UnloadingMsg.edit(content=f"<:error:724683693104562297> | Extension `{cog}` has not been loaded.")

@Client.command(hidden=True)
@commands.is_owner()
async def reload(ctx, cog: str):
	cog = cog.capitalize()
	if cog == "All":
		ReloadingMsg = await ctx.send(f"Reloading all extensions")
		for Extension in [f.replace('.py', '') for f in os.listdir("Cogs") if os.path.isfile(os.path.join("Cogs", f))]:
			if Extension in IgnoreImport:
				continue
			try:
				Client.unload_extension(f"Cogs.{Extension}")
				Client.load_extension(f"Cogs.{Extension}")
			except (discord.ClientException, ModuleNotFoundError):
				await ReloadingMsg.edit(content=f"<:error:724683693104562297> | Failed to unload extension `{Extension}`.")
			except commands.errors.ExtensionNotLoaded:
				await ReloadingMsg.edit(content=f"Loading extension `{Extension}`")
				Client.load_extension(f"Cogs.{Extension}")
				print(f"Extension {Extension} reloaded")
			except commands.errors.ExtensionNotFound:
				await ReloadingMsg.edit(content=f"<:error:724683693104562297> | Extension `{Extension}` does not exist.")
		await ReloadingMsg.edit(content="All extensions reloaded.")
	else:
		try:
			ReloadingMsg = await ctx.send(f"Reloading extension `{cog}`")
			Client.unload_extension(f"Cogs.{cog}")
			Client.load_extension(f"Cogs.{cog}")
			await ReloadingMsg.edit(content=f"Extension `{cog}` reloaded.")
			print(f"Extension {cog} reloaded")
		except (discord.ClientException, ModuleNotFoundError):
			await ReloadingMsg.edit(content=f"<:error:724683693104562297> | Failed to unload extension `{cog}`.")
		except commands.errors.ExtensionNotLoaded:
			await ReloadingMsg.edit(content=f"Loading extension `{cog}`")
			Client.load_extension(f"Cogs.{cog}")
			await ReloadingMsg.edit(content=f"Extension `{cog}` reloaded.")
			print(f"Extension {cog} reloaded")
		except commands.errors.ExtensionNotFound:
			await ctx.send(f"<:error:724683693104562297> | Extension `{cog}` does not exist.")

@Client.command(hidden=True)
@commands.is_owner()
async def restart(ctx):
	await ctx.send("Restarting bot.")
	ChangePresence.cancel()
	await Client.change_presence(
		status=discord.Status.offline,
		afk=True
		)
	os.execv(sys.executable, ['python'] + sys.argv)
	await Client.close()
	while not Client.is_closed():
		_ = True
	sys.exit()

@Client.command(hidden=True)
@commands.is_owner()
async def shutdown(ctx):
	await ctx.send("Shutting down bot.")
	ChangePresence.cancel()
	await Client.change_presence(
		status=discord.Status.offline,
		afk=True
		)
	await Client.close()
	while not Client.is_closed():
		_ = True
	os._exit(1)

@Client.command(hidden=True)
@commands.is_owner()
async def emotes(ctx):
	await ctx.send(f"""All emotes:\nLoading: <a:loading:725022752150519941> \\<a:loading:725022752150519941>
ProtoPoints: <:protopoints:724613134198767646> \\<:protopoints:724613134198767646>
Error: <:error:724683693104562297> \\<:error:724683693104562297>
Love: <:love:724686092669943858> \\<:love:724686092669943858>""")

@Client.command(hidden=True)
@commands.is_owner()
async def globalblacklist(ctx, Member: discord.Member, Reason: typing.Optional[str] = None):
	BlacklistCursor.execute("SELECT Reason FROM blacklist WHERE UserID = ?",(Member.id,))
	Reason = BlacklistCursor.fetchone()
	if Reason == None:
		BlacklistCursor.execute("INSERT INTO blacklist(UserID, Reason) VALUES(?,?)",(Member.id, Reason))
		BlacklistDB.commit()
		await ctx.send(f"{Member.mention} has been blacklisted from using ProtoBot.")
	else:
		BlacklistCursor.execute("DELETE FROM blacklist WHERE UserID = ?",(Member.id,))
		BlacklistDB.commit()
		await ctx.send(f"{Member.mention} has been removed from the ProtoBot blacklist.")

@Client.event
async def on_ready():
	print(f"=-=-=-=-=-=-=\nProtoBot v{Config['Settings']['Version']} started\nLogged in as: {Client.user.name} - {Client.user.id}\n=-=-=-=-=-=-=")
	ChangePresence.start()

Client.run("token")
