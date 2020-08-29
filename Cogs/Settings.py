import discord, sqlite3, configparser, os
from discord.ext import commands
from discord.utils import get
from CheckBlacklist import CheckBlacklist

class Settings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.SettingsDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}ServerSettings.db")
		self.SettingsCursor = self.SettingsDB.cursor()
		self.Config = configparser.ConfigParser()
		self.Config.read(f".{os.path.sep}Config{os.path.sep}config.ini")
		self.IgnoreDisable = ["disable","enable"]

	@commands.command(help="Shows the current prefix and set the prefix\nRequired perms:\nManage Server")
	@commands.has_permissions(manage_guild=True)
	async def prefix(self, ctx, *prefix: str):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		GuildID = ctx.guild.id
		if prefix == ():
			self.SettingsCursor.execute("SELECT prefix FROM prefix WHERE GuildID = ?",(GuildID,))
			self.CurrentPrefix = self.SettingsCursor.fetchone()
			if self.CurrentPrefix == None:
				self.CurrentPrefix = self.Config["Settings"]["Prefix"]
			else:
				self.CurrentPrefix = self.CurrentPrefix[0]
			await ctx.send(f"The current prefix is {self.CurrentPrefix} (p+ and mentioning will always work)")
			return
		self.SettingsCursor.execute("SELECT prefix FROM prefix WHERE GuildID = ?",(GuildID,))
		self.CurrentPrefix = self.SettingsCursor.fetchone()
		if self.CurrentPrefix == None:
			self.SettingsCursor.execute("INSERT INTO prefix(GuildID, prefix) VALUES (?,?)",(GuildID, prefix[0]))
		else:
			self.SettingsCursor.execute("UPDATE prefix SET prefix = ? WHERE GuildID = ?",(prefix[0], GuildID))
		self.SettingsDB.commit()
		await ctx.send(f"The prefix has been updated to {prefix[0]}")

	@commands.command(help="View the muted role and set muted role\nRequired perms:\nManage Server")
	@commands.has_permissions(manage_guild=True)
	async def mutedrole(self, ctx, *role: discord.Role):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		GuildID = ctx.guild.id
		if role == ():
			self.SettingsCursor.execute("SELECT RoleID FROM mutedrole WHERE GuildID = ?",(GuildID,))
			self.CurrentMutedRole = self.SettingsCursor.fetchone()
			if self.CurrentMutedRole == None:
				await ctx.send("<:error:724683693104562297> | There is no muted role for this server.")
			else:
				self.CurrentMutedRole = self.CurrentMutedRole[0]
				RoleObj = get(ctx.guild.roles, id=self.CurrentMutedRole)
				await ctx.send(f"The muted role for this server is {RoleObj.mention}.")
			return
		self.SettingsCursor.execute("SELECT RoleID FROM mutedrole WHERE GuildID = ?",(GuildID,))
		self.CurrentMutedRole = self.SettingsCursor.fetchone()
		role = int(role[0].id)
		if self.CurrentMutedRole == None:
			self.SettingsCursor.execute("INSERT INTO mutedrole(GuildID, RoleID) VALUES (?,?)",(GuildID, role))
		else:
			self.SettingsCursor.execute("UPDATE mutedrole SET RoleID = ? WHERE GuildID = ?",(role, GuildID))
		self.SettingsDB.commit()
		RoleObj = get(ctx.guild.roles, id=role)
		await ctx.send(f"The muted role has been updated to {RoleObj.mention}.")

	@commands.command(help="Disable a command for your server\nRequired perms:\nManage Server")
	@commands.has_permissions(manage_guild=True)
	async def disable(self, ctx, CommandName: str):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CommandName.lower() in self.IgnoreDisable:
			await ctx.send(f"<:error:724683693104562297> | You are not allowed to disable {CommandName.capitalize()}.")
			return
		if self.bot.get_command(CommandName.lower()) == None:
			await ctx.send(f"<:error:724683693104562297> | {CommandName.capitalize()} is not a command.")
			return
		self.SettingsCursor.execute("SELECT Disabled FROM disabledcommands WHERE GuildID = ?",(ctx.guild.id,))
		Disabled = self.SettingsCursor.fetchone()
		OrigDisabled = Disabled
		if Disabled == None or Disabled[0] == "":
			Disabled = [CommandName.lower()]
		else:
			Disabled = Disabled[0].split(",")
			for Command in Disabled:
				if Command.lower() == CommandName.lower():
					await ctx.send(f"<:error:724683693104562297> | {CommandName.capitalize()} is already disabled.")
					return
			Disabled.append(CommandName.lower())
		Disabled = ",".join(Disabled)
		if OrigDisabled == None:
			self.SettingsCursor.execute("INSERT INTO disabledcommands(GuildID, Disabled) VALUES(?,?)",(ctx.guild.id, Disabled))
		else:
			self.SettingsCursor.execute("UPDATE disabledcommands SET Disabled = ? Where GuildID = ?",(Disabled, ctx.guild.id))
		self.SettingsDB.commit()
		await ctx.send(f"{CommandName.capitalize()} is now disabled.")

	@commands.command(help="Enable a command for your server\nRequired perms:\nManage Server")
	@commands.has_permissions(manage_guild=True)
	async def enable(self, ctx, CommandName: str):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if self.bot.get_command(CommandName.lower()) == None:
			await ctx.send(f"<:error:724683693104562297> | {CommandName.capitalize()} is not a command.")
			return
		self.SettingsCursor.execute("SELECT Disabled FROM disabledcommands WHERE GuildID = ?",(ctx.guild.id,))
		Disabled = self.SettingsCursor.fetchone()
		OrigDisabled = Disabled
		if Disabled == None or Disabled[0] == "":
			await ctx.send(f"<:error:724683693104562297> | {CommandName.capitalize()} is not disabled.")
			return
		else:
			Disabled = Disabled[0].split(",")
			Removed = False
			for Command in Disabled:
				if Command.lower() == CommandName.lower():
					Disabled.remove(Command)
					Removed = True
		if not Removed:
			await ctx.send(f"<:error:724683693104562297> | {CommandName.capitalize()} is not disabled.")
			return
		Disabled = ",".join(Disabled)
		self.SettingsCursor.execute("UPDATE disabledcommands SET Disabled = ? WHERE GuildID = ?",(Disabled, ctx.guild.id))
		self.SettingsDB.commit()
		await ctx.send(f"{CommandName.capitalize()} is now enabled.")

	@commands.command(help="Sets the role to give to new members using the role's ID\nRequired Perms:\nManage Server")
	@commands.has_permissions(manage_guild=True)
	async def joinrole(self, ctx, RoleID: int):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "joinrole"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		self.SettingsCursor.execute("SELECT RoleID FROM joinrole WHERE GuildID = ?",(ctx.guild.id,))
		JoinRole = self.SettingsCursor.fetchone()
		if JoinRole == None:
			self.SettingsCursor.execute("INSERT INTO joinrole(RoleID, GuildID) VALUES(?,?)",(RoleID, ctx.guild.id))
		else:
			self.SettingsCursor.execute("UPDATE joinrole SET RoleID = ? WHERE GuildID = ?", (RoleID, ctx.guild.id))
		self.SettingsDB.commit()
		await ctx.send(f"The joinrole has been set to {Role}. New members will recieve this role.")

def setup(bot):
	bot.add_cog(Settings(bot))
