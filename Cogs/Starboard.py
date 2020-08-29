import discord, sqlite3, datetime, os
from discord.ext import commands
from humanfriendly import format_timespan
from CheckDisabled import CheckDisabled
from CheckBlacklist import CheckBlacklist

class Starboard(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.SettingsDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}ServerSettings.db")
		self.SettingsCursor = self.SettingsDB.cursor()
		self.StarboardDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}Starboard.db")
		self.StarboardCursor = self.StarboardDB.cursor()

	@commands.command(help="Set a starboard channel\nRequired perms:\n`Manage Messages`")
	@commands.has_permissions(manage_messages=True)
	async def starboardchannel(self, ctx, StarboardChannel: discord.TextChannel):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "starboardchannel"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		self.SettingsCursor.execute("SELECT ChannelID FROM starboard WHERE GuildID = ?",(ctx.guild.id,))
		ChannelID = self.SettingsCursor.fetchone()
		if ChannelID == None:
			self.SettingsCursor.execute("INSERT INTO starboard(GuildID, ChannelID, StarAmount) VALUES(?,?,?)",(ctx.guild.id, StarboardChannel.id, 3))
			self.SettingsDB.commit()
			await ctx.send(f"Starboard channel set to {StarboardChannel.mention}. 3 stars are required to get on the starboard.")
			return
		self.SettingsCursor.execute("UPDATE starboard SET ChannelID = ? WHERE GuildID = ?",(StarboardChannel.id, ctx.guild.id))
		self.SettingsDB.commit()
		await ctx.send(f"Starboard channel set to {StarboardChannel.mention}. 3 stars are required to get on the starboard.")

	@commands.command(help="Set the minimum amount of stars to get on the starboard\nRequired perms:\n`Manage Messages`")
	@commands.has_permissions(manage_messages=True)
	async def minimumstars(self, ctx, MinimumStars: int):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "minimumstars"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		self.SettingsCursor.execute("SELECT ChannelID FROM starboard WHERE GuildID = ?",(ctx.guild.id,))
		ChannelID = self.SettingsCursor.fetchone()
		if ChannelID == None:
			await ctx.send("<:error:724683693104562297> | You must set a starboard channel first.")
			return
		self.SettingsCursor.execute("UPDATE starboard SET StarAmount = ? WHERE GuildID = ?",(MinimumStars, ctx.guild.id))
		self.SettingsDB.commit()
		await ctx.send(f"Minimum stars set. {MinimumStars} stars are required to get on the starboard.")

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if payload.emoji.name == "⭐":
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			self.StarboardCursor.execute("SELECT Stars FROM starboard WHERE MsgID = ?",(payload.message_id,))
			MsgStars = self.StarboardCursor.fetchone()
			NotExist = False
			if MsgStars == None:
				MsgStars = 0
				NotExist = True
			else:
				MsgStars = MsgStars[0]
			if message.author.id == payload.user_id:
				await message.remove_reaction(payload.emoji, payload.member)
				await payload.member.send("<:error:724683693104562297> | You cannot star your own message.")
				return
			elif self.bot.get_user(payload.user_id).bot:
				return
			elif message.author.bot:
				await message.remove_reaction(payload.emoji, payload.member)
				await payload.member.send("<:error:724683693104562297> | You cannot star a bot's message.")
				return
			MsgStars += 1
			if NotExist:
				self.StarboardCursor.execute("INSERT INTO starboard(MsgID, Stars, MsgSent, MsgSentID) VALUES(?,?,?,?)",(payload.message_id, MsgStars, 0, 0))
			else:
				self.StarboardCursor.execute("UPDATE starboard SET Stars = ? WHERE MsgID = ?",(MsgStars, payload.message_id))
			self.StarboardDB.commit()
			self.SettingsCursor.execute("SELECT StarAmount FROM starboard WHERE GuildID = ?",(payload.guild_id,))
			StarAmount = self.SettingsCursor.fetchone()
			if StarAmount == None:
				return
			StarAmount = StarAmount[0]
			if MsgStars >= StarAmount:
				self.StarboardCursor.execute("SELECT MsgSent FROM starboard WHERE MsgID = ?",(payload.message_id,))
				MsgSent = self.StarboardCursor.fetchone()
				if MsgSent == None:
					return
				MsgSent = MsgSent[0]
				self.SettingsCursor.execute("SELECT ChannelID FROM starboard WHERE GuildID = ?",(payload.guild_id,))
				ChannelID = self.SettingsCursor.fetchone()
				if ChannelID == None:
					return
				if payload.channel_id == ChannelID[0]:
					await message.remove_reaction(payload.emoji, payload.member)
					await payload.member.send("<:error:724683693104562297> | You cannot star a message in the starboard channel.")
					return
				StarboardChannel = self.bot.get_channel(ChannelID[0])
				StarboardEmbed = discord.Embed(title="Starred Message", timestamp=datetime.datetime.utcnow())
				StarboardEmbed.add_field(name="Author:", value=f"{message.author.mention}", inline=False)
				StarboardEmbed.add_field(name="Content:", value=message.content or "No content.", inline=False)
				StarboardEmbed.add_field(name="Stars:", value=MsgStars, inline=False)
				if len(message.attachments):
					StarboardEmbed.set_image(url=message.attachments[0].url)
				if MsgSent == 0:
					StarMsg = await StarboardChannel.send("",embed=StarboardEmbed)
				else:
					self.StarboardCursor.execute("SELECT MsgSentID FROM starboard WHERE MsgID = ?",(payload.message_id,))
					StarMsgID = self.StarboardCursor.fetchone()
					StarMsgID = StarMsgID[0]
					StarMsg = await StarboardChannel.fetch_message(StarMsgID)
					await StarMsg.edit(embed=StarboardEmbed)
				self.StarboardCursor.execute("UPDATE starboard SET MsgSent = ? WHERE MsgID = ?",(1, payload.message_id))
				self.StarboardCursor.execute("UPDATE starboard SET MsgSentID = ? WHERE MsgID = ?",(StarMsg.id, payload.message_id))
				self.StarboardDB.commit()

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if payload.emoji.name == "⭐":
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			self.StarboardCursor.execute("SELECT Stars FROM starboard WHERE MsgID = ?",(payload.message_id,))
			MsgStars = self.StarboardCursor.fetchone()[0]
			MsgStars -= 1
			self.StarboardCursor.execute("UPDATE starboard SET Stars = ? WHERE MsgID = ?",(MsgStars, payload.message_id))
			self.StarboardDB.commit()
			self.SettingsCursor.execute("SELECT StarAmount FROM starboard WHERE GuildID = ?",(payload.guild_id,))
			StarAmount = self.SettingsCursor.fetchone()[0]
			if MsgStars >= StarAmount:
				self.StarboardCursor.execute("SELECT MsgSent FROM starboard WHERE MsgID = ?",(payload.message_id,))
				MsgSent = self.StarboardCursor.fetchone()
				if MsgSent == None:
					return
				MsgSent = MsgSent[0]
				self.SettingsCursor.execute("SELECT ChannelID FROM starboard WHERE GuildID = ?",(payload.guild_id,))
				ChannelID = self.SettingsCursor.fetchone()
				if ChannelID == None:
					return
				StarboardChannel = self.bot.get_channel(ChannelID[0])
				StarboardEmbed = discord.Embed(title="Starred Message", timestamp=datetime.datetime.utcnow())
				StarboardEmbed.add_field(name="Author:", value=f"{message.author.mention}", inline=False)
				StarboardEmbed.add_field(name="Content:", value=message.content or "No content.", inline=False)
				StarboardEmbed.add_field(name="Stars:", value=MsgStars, inline=False)
				if len(message.attachments):
					StarboardEmbed.set_image(url=message.attachments[0].url)
				if MsgSent == 0:
					StarMsg = await StarboardChannel.send("",embed=StarboardEmbed)
				else:
					self.StarboardCursor.execute("SELECT MsgSentID FROM starboard WHERE MsgID = ?",(payload.message_id,))
					StarMsgID = self.StarboardCursor.fetchone()
					StarMsgID = StarMsgID[0]
					StarMsg = await StarboardChannel.fetch_message(StarMsgID)
					await StarMsg.edit(embed=StarboardEmbed)
				self.StarboardCursor.execute("UPDATE starboard SET MsgSent = ? WHERE MsgID = ?",(1, payload.message_id))
				self.StarboardCursor.execute("UPDATE starboard SET MsgSentID = ? WHERE MsgID = ?",(StarMsg.id, payload.message_id))
				self.StarboardDB.commit()
			else:
				self.SettingsCursor.execute("SELECT ChannelID FROM starboard WHERE GuildID = ?",(payload.guild_id,))
				ChannelID = self.SettingsCursor.fetchone()
				if ChannelID == None:
					return
				StarboardChannel = self.bot.get_channel(ChannelID[0])
				self.StarboardCursor.execute("SELECT MsgSentID FROM starboard WHERE MsgID = ?",(payload.message_id,))
				StarMsgID = self.StarboardCursor.fetchone()
				StarMsgID = StarMsgID[0]
				StarMsg = await StarboardChannel.fetch_message(StarMsgID)
				await StarMsg.delete()
				self.StarboardCursor.execute("UPDATE starboard SET MsgSent = ? WHERE MsgID = ?",(0, payload.message_id))
				self.StarboardCursor.execute("UPDATE starboard SET MsgSentID = ? WHERE MsgID = ?",(0, payload.message_id))
				self.StarboardDB.commit()

def setup(bot):
	bot.add_cog(Starboard(bot))
