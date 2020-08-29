import discord, time, random, requests
from discord.ext import commands
from CheckDisabled import CheckDisabled
from CheckBlacklist import CheckBlacklist

class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.BallChoices = ["Definitely","Possibly","Maybe","Maybe not","Concentrate and ask later","Ask again later","Definitely not","Cannot predict now","Very doubtful","Better not tell you now","Reply hazy try again"]

	@commands.command(help="Ask the 8ball a question")
	async def ball(self, ctx):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "ball"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		await ctx.send(random.choice(self.BallChoices))

	@commands.command(help="Chooses between specified options\nOptions must be split with `|`")
	async def choose(self, ctx, *options):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "choose"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		options = " ".join(options)
		options = options.split("|")
		if len(options) == 1:
			await ctx.send("<:error:724683693104562297> | You need to specify at least 2 items!")
			return
		await ctx.send(f":thinking: {ctx.author.mention} | I choose {random.choice(options)}")

	@commands.command(help="Tells you if you are cool or not")
	async def cool(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "cool"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if member == ():
			member = ctx.author
		else:
			member = member[0]
		if random.randint(0,1) == 0:
			await ctx.send(f"{member.mention} is cool :sunglasses:")
		else:
			await ctx.send(f"{member.mention} isn't cool :(")

	@commands.command(help="Reports someone")
	async def report(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "report"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if member == ():
			member = ctx.author
		else:
			member = member[0]
		await ctx.send(f"{member.mention} has been reported to the appropriate authorities.")

	@commands.command(help="Gets a random dog photo\nCan specify a breed to get a random photo of that breed.")
	async def dog(self, ctx, *breed: str):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "dog"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		DogMsg = await ctx.send("Getting your dog...")
		if breed != ():
			breed = breed[0]
			DogReq = requests.get(f"https://dog.ceo/api/breed/{breed}/images/random")
			DogJson = DogReq.json()
			if DogJson["status"] == "error":
				await ctx.send(f"<:error:724683693104562297> | There was an error.\nError message:\n{DogJson['message']}")
				return
			await DogMsg.edit(content=f"Here is your random {breed}:\n{DogJson['message']}")
		else:
			DogReq = requests.get(f"https://dog.ceo/api/breeds/image/random")
			DogJson = DogReq.json()
			if DogJson["status"] == "error":
				await ctx.send(f"<:error:724683693104562297> | There was an error.\nError message:\n{DogJson['message']}")
				return
			await DogMsg.edit(content=f"Here is your random dog:\n{DogJson['message']}")

	@commands.command(help="Gets a random cat photo")
	async def cat(self, ctx):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "cat"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		CatMsg = await ctx.send("Getting your random cat...")
		CatHeader = {"x-api-header":"6ef3130a-1a12-4c82-aff2-95a3c3f7420a"}
		CatReq = requests.get("https://api.thecatapi.com/v1/images/search", headers=CatHeader)
		CatReq = CatReq.json()
		URL = CatReq[0]["url"]
		await CatMsg.edit(content=f"Here is your random cat:\n{URL}")

	@commands.command(help="Gets a random duck photo/gif")
	async def duck(self, ctx):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "duck"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		DuckMsg = await ctx.send("Getting your random duck...")
		DuckReq = requests.get("https://random-d.uk/api/v2/quack")
		DuckReq = DuckReq.json()
		URL = DuckReq["url"]
		await DuckMsg.edit(content=f"Here is your random duck photo:\n{URL}")

	@commands.command(help="Rolls a dice with format `dnd`\nMax 10 dice.")
	async def roll(self, ctx, dice: str):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "roll"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if dice == ():
			await ctx.send("<:error:724683693104562297> | You need to specify a dice to roll in format {amount}n{dicemax}")
			return
		dice = dice[0]
		dice = dice.split("n")
		if len(dice) != 2:
			await ctx.send("<:error:724683693104562297> | You need to specify a dice to roll in format {amount}n{dicemax}")
		amount = int(dice[0])
		if amount > 25:
			await ctx.send("<:error:724683693104562297> | This is too many dice. Please reduce it to under 10.")
			return
		max = int(dice[1])
		if max > 100:
			await ctx.send("<:error:724683693104562297> | The max is too big. Please reduce it to under 100.")
			return
		RandDice = []
		for _ in range(amount):
			RandDice.append(str(random.randint(1,max)))
		DiceEmbed = discord.Embed(title=f"Rolling {amount} dice", description="\n".join(RandDice))
		await ctx.send("Here are the dice results:", embed = DiceEmbed)

	@commands.command(help="Flip a coin")
	async def coin(self, ctx):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "coin"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		Options = ["heads", "tails"]
		await ctx.send(f"Its {random.choice(Options)}!")

	@commands.command(help="Highfives someone")
	async def highfive(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "highfive"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if member == ():
			member = ctx.author
		else:
			member = member[0]
		await ctx.send(f"Highfives {member.mention} :hand_splayed:")

def setup(bot):
	bot.add_cog(Fun(bot))
