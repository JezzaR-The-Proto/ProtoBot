import discord, sqlite3, os
from discord.ext import commands
from discord.utils import get
from CheckDisabled import CheckDisabled
from CheckBlacklist import CheckBlacklist

class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.SettingsDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}ServerSettings.db")
		self.SettingsCursor = self.SettingsDB.cursor()

	@commands.command(help="Kicks the mentioned member")
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, member: discord.Member, *reason):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "kick"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		KickMsg = await ctx.send(f"<a:loading:725022752150519941> | Attempting to kick {member.mention}")
		if reason == ():
			await ctx.guild.kick(member, reason=f"Kicked by {ctx.author}")
			await KickMsg.edit(content=f"`{member}` was kicked by {ctx.author.mention} without a reason.")
		else:
			reason = " ".join(reason)
			await ctx.guild.kick(member, reason=f"Kicked by {ctx.author} for {reason}")
			await KickMsg.edit(content=f"`{member}` was kicked by {ctx.author.mention} for `{reason}`")

	@commands.command(help="Bans the mentioned member")
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: discord.Member, *reason):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "ban"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		BanMsg = await ctx.send(f"<a:loading:725022752150519941> | Attempting to ban {member.mention}")
		if reason == ():
			await ctx.guild.ban(member, reason=f"Banned by {ctx.author}")
			await BanMsg.edit(content=f"`{member}` was banned by {ctx.author.mention} without a reason.")
		else:
			reason = " ".join(reason)
			await ctx.guild.ban(member, reason=f"Banned by {ctx.author} for {reason}")
			await BanMsg.edit(content=f"`{member}` was banned by {ctx.author.mention} for `{reason}`")

	@commands.command(help="Unbans a member using ID")
	@commands.has_permissions(ban_members=True)
	async def unban(self, ctx, ID: int, *reason):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "ban"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		BanMsg = await ctx.send(f"<a:loading:725022752150519941> | Attempting to unban {ID}")
		UnbanTarget = None
		async for entry in ctx.guild.audit_logs(action=discord.AuditLogAction.ban):
			if entry.target.id == ID:
				if reason == ():
					await ctx.guild.unban(entry.target, f"Unbanned by {ctx.author} without a reason.")
				else:
					reason = " ".join(reason)
					await ctx.guild.unban(entry.target, f"Unbanned by {ctx.author} for {reason}.")
				UnbanTarget = entry.target
				break
		if UnbanTarget:
			await BanMsg.edit(content=f"User {UnbanTarget} has been unbanned.")
		else:
			await BanMsg.edit(content=f"<:error:724683693104562297> | {ID} couldn't be unbanned.")

	@commands.command(help="Clears the number of messages\nMax 500 messages.")
	@commands.has_permissions(manage_messages=True)
	async def purge(self, ctx, amount: int):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "purge"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if amount > 100:
			await ctx.send("<:error:724683693104562297> | That is too many messages.")
			return
		await ctx.channel.purge(limit=amount)
		await ctx.send(f"{amount} messages cleared.", delete_after=15)

	@commands.command(help="Mutes the mentioned member\nRequired Roles:\n`Manage Roles`")
	@commands.has_permissions(manage_messages=True)
	async def mute(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "mute"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		GuildID = ctx.guild.id
		self.SettingsCursor.execute("SELECT RoleID FROM mutedrole WHERE GuildID = ?",(GuildID,))
		self.MutedRole = self.SettingsCursor.fetchone()
		if self.MutedRole == None:
			await ctx.send("<:error:724683693104562297> | I cannot mute people if there is no muted role.")
			return
		if member == ():
			await ctx.send("<:error:724683693104562297> | You need to mention who to mute.")
			return
		member = member[0]
		self.MutedRole = int(self.MutedRole[0])
		RoleObj = get(ctx.guild.roles, id=self.MutedRole)
		if RoleObj in member.roles:
			await ctx.send(f"<:error:724683693104562297> | {member.mention} is already muted. I cannot mute them again.")
			return
		await member.add_roles(RoleObj)
		await ctx.send(f"Added the muted role to {member.mention}")

	@commands.command(help="Unmutes the mentioned member\nRequired Roles:\n`Manage Roles`")
	@commands.has_permissions(manage_messages=True)
	async def unmute(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "unmute"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		GuildID = ctx.guild.id
		self.SettingsCursor.execute("SELECT RoleID FROM mutedrole WHERE GuildID = ?",(GuildID,))
		self.MutedRole = self.SettingsCursor.fetchone()
		if self.MutedRole == None:
			await ctx.send("<:error:724683693104562297> | I cannot unmute people if there is no muted role.")
			return
		if member == ():
			await ctx.send("<:error:724683693104562297> | You need to mention who to unmute.")
			return
		member = member[0]
		self.MutedRole = int(self.MutedRole[0])
		RoleObj = get(ctx.guild.roles, id=self.MutedRole)
		if RoleObj not in member.roles:
			await ctx.send(f"<:error:724683693104562297> | {member.mention} is not muted with my mute role. I cannot unmute them.")
			return
		await member.remove_roles(RoleObj)
		await ctx.send(f"Removed the muted role from {member.mention}")

	@commands.command(help="Adds/removes a word from the blacklist or views it\nRequired Perms:\n`Manage Roles`")
	@commands.has_permissions(manage_roles=True)
	async def blacklist(self, ctx, *word: str):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "blacklist"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if word == ():
			self.SettingsCursor.execute("SELECT Words FROM blacklist WHERE GuildID = ?",(ctx.guild.id,))
			Words = self.SettingsCursor.fetchone()
			if Words == None:
				self.SettingsCursor.execute("INSERT INTO blacklist(GuildID, Words) VALUES(?,?)",(ctx.guild.id,""))
				self.SettingsDB.commit()
				await ctx.send("<:error:724683693104562297> | There is no blacklist on this server.")
				return
			if Words[0] == "":
				await ctx.send("<:error:724683693104562297> | There is no blacklist on this server.")
				return
			Words = Words[0]
			BLArray = Words.split(",")
			BLEmbed = discord.Embed(title=f"Blacklist for {ctx.guild}", description=f"Amount: {len(BLArray)}")
			x = 0
			while x < len(BLArray):
				try:
					BLEmbed.add_field(name=f"{BLArray[x]}", value=f"{BLArray[x + 1]}")
					x += 2
				except IndexError:
					BLEmbed.add_field(name=f"{BLArray[x]}", value="\uFEFF")
					x += 1
			await ctx.send("", embed=BLEmbed)
			return
		word = word[0]
		if "," in word:
			await ctx.send("<:error:724683693104562297> | You cannot blacklist anything with a comma in.")
			return
		self.SettingsCursor.execute("SELECT Words FROM blacklist WHERE GuildID = ?",(ctx.guild.id,))
		Words = self.SettingsCursor.fetchone()
		if Words == None or Words == "":
			Words = [word]
		else:
			Words = Words[0].split(",")
			Found = False
			for Word in Words:
				if Word == word:
					Words.remove(word)
					Found = True
			if not Found:
				Words.append(word)
		try:
			if Words[0] == "":
				del Words[0]
		except IndexError:
			pass
		Words = ",".join(Words)
		self.SettingsCursor.execute("UPDATE blacklist SET Words = ? WHERE GuildID = ?",(Words,ctx.guild.id))
		self.SettingsDB.commit()
		if Found:
			await ctx.send(f"{word} removed from the blacklist")
		else:
			await ctx.send(f"{word} added to the blacklist")

def setup(bot):
	bot.add_cog(Moderation(bot))
