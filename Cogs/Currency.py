import discord, sqlite3, typing, os
from discord.ext import commands
from CheckDisabled import CheckDisabled
from CheckBlacklist import CheckBlacklist

class Currency(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.CurrencyDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}Currency.db")
		self.CurrencyCursor = self.CurrencyDB.cursor()

	@commands.command(help="Check someone's balance\nDefaults to author if no person specified.")
	async def balance(self, ctx, *user: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "balance"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if user == ():
			user = ctx.author
		else:
			user = user[0]
		self.CurrencyCursor.execute("SELECT ProtoPoints FROM protopoints WHERE UserID = ?",(user.id,))
		ProtoPoints = self.CurrencyCursor.fetchone()
		if ProtoPoints == None:
			self.CurrencyCursor.execute("INSERT INTO protopoints(UserID, ProtoPoints) VALUES(?,?)",(user.id, 0))
			self.CurrencyDB.commit()
			await ctx.send(f"<:protopoints:724613134198767646> | {user.mention} has 0 ProtoPoints.")
			return
		ProtoPoints = ProtoPoints[0]
		await ctx.send(f"<:protopoints:724613134198767646> | {user.mention} has {ProtoPoints} ProtoPoints.")

	@commands.command(help="Get your daily ProtoPoints\nResets after 24h")
	@commands.cooldown(1, 86400, commands.BucketType.user)
	async def daily(self, ctx):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "daily"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		self.CurrencyCursor.execute("SELECT ProtoPoints FROM protopoints WHERE UserID = ?",(ctx.author.id,))
		ProtoPoints = self.CurrencyCursor.fetchone()
		if ProtoPoints == None:
			self.CurrencyCursor.execute("INSERT INTO protopoints(UserID, ProtoPoints) VALUES(?,?)",(ctx.author.id, 100))
			self.CurrencyDB.commit()
			await ctx.send(f"<:protopoints:724613134198767646> | Daily claimed! {ctx.author.mention} now has 100 ProtoPoints.")
			return
		ProtoPoints = int(ProtoPoints[0])
		ProtoPoints += 100
		self.CurrencyCursor.execute("UPDATE protopoints SET ProtoPoints = ? WHERE UserID = ?",(ProtoPoints, ctx.author.id))
		self.CurrencyDB.commit()
		await ctx.send(f"<:protopoints:724613134198767646> | Daily claimed! {ctx.author.mention} now has {ProtoPoints} ProtoPoints.")

	@commands.command(help="Pay the mentioned person the specified amount")
	async def pay(self, ctx, User: discord.Member, Amount: int):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "pay"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		AuthorID = ctx.author.id
		UserID = User.id
		self.CurrencyCursor.execute("SELECT ProtoPoints FROM protopoints WHERE UserID = ?",(AuthorID,))
		AuthorProtoPoints = self.CurrencyCursor.fetchone()
		self.CurrencyCursor.execute("SELECT ProtoPoints FROM protopoints WHERE UserID = ?",(UserID,))
		UserProtoPoints = self.CurrencyCursor.fetchone()
		if AuthorProtoPoints == None or int(AuthorProtoPoints[0]) < Amount:
			await ctx.send("You do not have enough ProtoPoints to pay this amount.")
			return
		AuthorProtoPoints = int(AuthorProtoPoints[0])
		NonExistantUser = False
		if UserProtoPoints == None:
			UserProtoPoints = 0
			NonExistantUser = True
		else:
			UserProtoPoints = int(UserProtoPoints[0])
		AuthorProtoPoints -= Amount
		UserProtoPoints += Amount
		self.CurrencyCursor.execute("UPDATE protopoints SET ProtoPoints = ? WHERE UserID = ?",(AuthorProtoPoints, AuthorID))
		if NonExistantUser:
			self.CurrencyCursor.execute("INSERT INTO protopoints(UserID, ProtoPoints) VALUES(?,?)",(UserID, UserProtoPoints))
		else:
			self.CurrencyCursor.execute("UPDATE protopoints SET ProtoPoints = ? WHERE UserID = ?",(UserProtoPoints, UserID))
		self.CurrencyDB.commit()
		await ctx.send(f"{ctx.author.mention} ({AuthorProtoPoints} ProtoPoints) has paid {Amount} ProtoPoints to {User.mention} ({UserProtoPoints} ProtoPoints). ")

	@commands.command(help="Give someone 1 rep")
	@commands.cooldown(1, 86400, commands.BucketType.user)
	async def rep(self, ctx, Member: typing.Optional[discord.Member] = None):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "rep"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if Member == None:
			await ctx.send("You must mention someone to rep.")
			self.bot.get_command("rep").reset_cooldown(ctx)
			return
		self.CurrencyCursor.execute("SELECT Rep FROM rep WHERE UserID = ?",(Member.id,))
		UserRep = self.CurrencyCursor.fetchone()
		NonExistantUser = False
		if UserRep == None:
			NonExistantUser = True
			UserRep = 0
		else:
			UserRep = UserRep[0]
		UserRep += 1
		if NonExistantUser:
			self.CurrencyCursor.execute("INSERT INTO rep(UserID, Rep) VALUES(?,?)",(Member.id, UserRep))
		else:
			self.CurrencyCursor.execute("UPDATE rep SET Rep = ? WHERE UserID = ?",(UserRep, Member.id))
		self.CurrencyDB.commit()
		await ctx.send(f"You have repped {Member.mention}. They now have {UserRep} rep.")

	@commands.command(help="Get the leaderboard\nCan specify either `ProtoPoints` or `Rep` to get either leaderboard")
	async def leaderboard(self, ctx, Type: typing.Optional[str] = "ProtoPoints"):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if Type.lower() not in ["protopoints","rep"]:
			await ctx.send("That is not a valid leaderboard type.\nThe valid types are `protopoints` and `rep`")
		if Type.lower() == "protopoints":
			LeaderboardMsg = await ctx.send("<a:loading:725022752150519941> | Getting ProtoPoints leaderboard")
			self.CurrencyCursor.execute("SELECT UserID, ProtoPoints FROM protopoints")
			Leaderboard = self.CurrencyCursor.fetchall()
			Leaderboard.sort()
			LeaderboardEmbed = discord.Embed(title="Global ProtoPoints leaderboard")
			count = 0
			for User, Points in Leaderboard:
				UserID = User
				User = self.bot.get_user(User)
				if User == None:
					await ctx.send("There was an error getting one of the users on the leaderboard.\nI will send as far as I got.")
					await ctx.send("",embed=LeaderboardEmbed)
					print(f"There was an error getting one of the users on the leaderboard. ID: {UserID}")
					return
				if count < 10:
					LeaderboardEmbed.add_field(name=f"{User.name}#{User.discriminator}:",value=Points, inline=False)
					count += 1
				else:
					break
			await LeaderboardMsg.edit(content="",embed=LeaderboardEmbed)
		else:
			LeaderboardMsg = await ctx.send("<a:loading:725022752150519941> | Getting Rep leaderboard")
			self.CurrencyCursor.execute("SELECT UserID, Rep FROM rep")
			Leaderboard = self.CurrencyCursor.fetchall()
			Leaderboard.sort()
			LeaderboardEmbed = discord.Embed(title="Global Rep leaderboard")
			count = 0
			for User, Points in Leaderboard:
				UserID = User
				User = self.bot.get_user(User)
				if User == None:
					await ctx.send("There was an error getting one of the users on the leaderboard.\nI will send as far as I got.")
					await ctx.send("",embed=LeaderboardEmbed)
					print(f"There was an error getting one of the users on the leaderboard. ID: {UserID}")
					return
				if count < 10:
					LeaderboardEmbed.add_field(name=f"{User.name}#{User.discriminator}:",value=Points, inline=False)
					count += 1
				else:
					break
			await LeaderboardMsg.edit(content="",embed=LeaderboardEmbed)

def setup(bot):
	bot.add_cog(Currency(bot))
