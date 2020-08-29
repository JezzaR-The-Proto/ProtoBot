import discord, sqlite3, typing, requests, json
from discord.ext import commands, tasks
from CheckDisabled import CheckDisabled
from BackpackTF import Currency
from CheckBlacklist import CheckBlacklist

class Bptf(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.GetBPTF.start()

	@tasks.loop(minutes=15)
	async def GetBPTF(self):
		try:
			BPAPI = Currency(apikey="5ec8f1002e539a736b357ace")
			AllPrices = BPAPI.getAllPrices()
			""" Item Rarities:
			0: Normal
			1: Genuine
			2:
			3: Vintage
			4: Strange Unique
			5: Unusual
			6: Unique
			7:
			8:
			9: Self Made Community Sparkle
			10:
			11: Strange
			12:
			13: Haunted
			14: Collectors"""
			ItemRarities = ["Normal","Genuine","","Vintage","Strange Unique","Unusual","Unique","","","Self Made Community Sparkle","","Strange","","Haunted","Collectors"]
			USDGBPConvRate = requests.get("https://free.currencyconverterapi.com/api/v5/convert?q=USD_GBP&apiKey=7abd620d6fae9d4b638d")
			USDGBPConvRate = USDGBPConvRate.json()
			USDPrice = AllPrices['raw_usd_value']
			GBPPrice = round(USDPrice * float(USDGBPConvRate["results"]["USD_GBP"]["val"]),2)
			self.Currencies = ["usd","gbp"]
			self.RefPrice = {}
			self.RefPrice["usd"] = USDPrice
			self.RefPrice["gbp"] = GBPPrice
			ItemPrices = AllPrices["items"]
			rarityIndex = {}
			for item in ItemPrices:
				rarities = []
				for rarity in ItemPrices[item]["prices"]:
					rarities.append(ItemRarities[int(rarity)])
					if ItemRarities[int(rarity)] == "":
						print("*"*20+rarity)
						print(item)
				rarityIndex[item] = rarities
			self.Items = []
			for item in rarityIndex:
				self.Items.append(item)
			self.Rarities = []
			for item in self.Items:
				self.Rarities.append(rarityIndex[item])
		except:
			print("Error getting BPTF prices, disabling BPTF module.")
			self.bot.unload_extension("Cogs.Bptf")

	@commands.command(help="List qualities of a certain TF2 item\nQualities update every 15 minutes")
	async def qualities(self, ctx, *Weapon):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "qualities"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if Weapon == ():
			await ctx.send("<:error:724683693104562297> | You must specify a weapon to get the rarities for.")
			return
		Weapon = " ".join(Weapon)
		x = 0
		while x < len(self.Items):
			if self.Items[x].lower() == Weapon.lower():
				WeaponRarities = []
				for Rarity in self.Rarities[x]:
					WeaponRarities.append(Rarity)
				if len(WeaponRarities) > 1:
					Are = "are"
				else:
					Are = "is"
				RarityStr = ', '.join(WeaponRarities)
				await ctx.send(f"The rarities for the {Weapon} {Are} `{RarityStr}`")
				return
			x += 1
		await ctx.send("<:error:724683693104562297> | This weapon does not exist. Check you have spelt it correctly.")

	@commands.command(help="Gets the current price of Refined Metal in a currency\nCurrency defaults to `GBP`\nPrice updates every 15 minutes")
	async def refprice(self, ctx, Currency: typing.Optional[str] = "gbp"):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "refprice"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		for Money in self.Currencies:
			if Currency.lower() == Money.lower():
				await ctx.send(f"The price of ref in {Currency.upper()} is {self.RefPrice[Currency.lower()]}")
				return
		await ctx.send(f"<:error:724683693104562297> | {Currency} is not a supported currency.")

def setup(bot):
	bot.add_cog(Bptf(bot))
