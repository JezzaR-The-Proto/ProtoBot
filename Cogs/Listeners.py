import discord, sqlite3, time, random
from discord.ext import commands
from discord.utils import get

class Listeners(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.SettingsDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}ServerSettings.db")
		self.SettingsCursor = self.SettingsDB.cursor()
		self.CurrencyDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}Currency.db")
		self.CurrencyCursor = self.CurrencyDB.cursor()
		self.LastMsg = {}

	async def CheckBlacklist(self, ctx):
		GuildID = ctx.guild.id
		self.SettingsCursor.execute("SELECT Words FROM blacklist WHERE GuildID = ?",(GuildID,))
		Words = self.SettingsCursor.fetchone()
		if Words == None or Words[0] == "":
			return
		Words = Words[0]
		WordList = Words.split(",")
		self.SettingsCursor.execute("SELECT RoleID FROM mutedrole WHERE GuildID = ?",(GuildID,))
		MuteRole = self.SettingsCursor.fetchone()
		if MuteRole == "" or MuteRole == None:
			return
		MuteRole = int(MuteRole[0])
		UserID = self.bot.user.id
		if "p+" in ctx.content.lower()[:2] or f"<@{UserID}" in ctx.content.lower()[:len(f"<@{UserID}")] or f"<@!{UserID}" in ctx.content.lower()[:len(f"<@!{UserID}")]:
			return
		if ctx.author.bot:
			return
		if ctx.guild:
			GuildID = ctx.guild.id
			self.SettingsCursor.execute("SELECT prefix FROM prefix WHERE GuildID = ?",(GuildID,))
			ServerPrefix = self.SettingsCursor.fetchone()
			if ServerPrefix != None:
				Prefix = ServerPrefix[0]
				if Prefix.lower() in ctx.content.lower()[:len(Prefix.lower())]:
					return
		for Word in WordList:
			if Word.lower() in ctx.content.lower():
				await ctx.delete()
				RoleObj = get(ctx.guild.roles, id=MuteRole)
				await ctx.author.add_roles(RoleObj)
				await ctx.author.send(f"<:error:724683693104562297> | You broke the blacklist on `{ctx.guild}`. The word found was `{Word.lower()}`. Ask an admin to be unmuted.")

	async def GiveTalkCredits(self, ctx):
		if ctx.author.bot:
			return
		GuildID = ctx.guild.id
		try:
			UserLastMsg = self.LastMsg[ctx.author.id]
			if UserLastMsg + 60 < time.time():
				self.CurrencyCursor.execute("SELECT ProtoPoints FROM protopoints WHERE UserID = ?",(ctx.author.id,))
				ProtoPoints = self.CurrencyCursor.fetchone()
				if ProtoPoints == None:
					ProtoPoints = random.randint(1,5)
					self.CurrencyCursor.execute("INSERT INTO protopoints(UserID, ProtoPoints) VALUES(?,?)",(ctx.author.id, ProtoPoints))
					self.CurrencyDB.commit()
				else:
					ProtoPoints = ProtoPoints[0]
					ProtoPoints += random.randint(1,5)
					self.CurrencyCursor.execute("UPDATE protopoints SET ProtoPoints = ? WHERE UserID = ?",(ProtoPoints, ctx.author.id))
					self.CurrencyDB.commit()
				self.LastMsg[ctx.author.id] = time.time()
		except KeyError:
			self.CurrencyCursor.execute("SELECT ProtoPoints FROM protopoints WHERE UserID = ?",(ctx.author.id,))
			ProtoPoints = self.CurrencyCursor.fetchone()
			if ProtoPoints == None:
				ProtoPoints = random.randint(1,5)
				self.CurrencyCursor.execute("INSERT INTO protopoints(UserID, ProtoPoints) VALUES(?,?)",(ctx.author.id, ProtoPoints))
				self.CurrencyDB.commit()
			else:
				ProtoPoints = ProtoPoints[0]
				ProtoPoints += random.randint(1,5)
				self.CurrencyCursor.execute("UPDATE protopoints SET ProtoPoints = ? WHERE UserID = ?",(ProtoPoints, ctx.author.id))
				self.CurrencyDB.commit()
			self.LastMsg[ctx.author.id] = time.time()

	@commands.Cog.listener()
	async def on_message(self, ctx):
		if not ctx.guild:
			return
		GuildID = ctx.guild.id
		await self.CheckBlacklist(ctx)
		await self.GiveTalkCredits(ctx)

	@commands.Cog.listener()
	async def on_member_join(self, ctx):
		self.SettingsCursor.execute("SELECT RoleID FROM joinrole WHERE GuildID = ?",(ctx.guild.id,))
		JoinRole = self.SettingsCursor.fetchone()
		if JoinRole != None:
			Role = ctx.guild.get_role(JoinRole[0])
			await ctx.add_roles(Role, "Join role")

def setup(bot):
	bot.add_cog(Listeners(bot))
