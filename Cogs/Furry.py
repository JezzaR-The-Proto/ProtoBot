import discord
from discord.ext import commands
from CheckDisabled import CheckDisabled
from CheckBlacklist import CheckBlacklist

class Furry(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(help="Tackles someone")
	async def tackle(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "tackle"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if member == ():
			member = ctx.author
		else:
			member = member[0]
		await ctx.send(f"Tackles {member.mention}")

	@commands.command(help="Boops someone :3")
	async def boop(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "boop"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if member == ():
			member = ctx.author
		else:
			member = member[0]
		await ctx.send(f"Boops {member.mention} :3")

	@commands.command(help="Hugs someone <3")
	async def hug(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "hug"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if member == ():
			member = ctx.author
		else:
			member = member[0]
		await ctx.send(f"Hugs {member.mention} <3")

	@commands.command(help="Noms someone\nDon't nom too hard!")
	async def nom(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "nom"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if member == ():
			member = ctx.author
		else:
			member = member[0]
		await ctx.send(f"Noms {member.mention}")

	@commands.command(help="Kisses someone <3")
	async def kiss(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "kiss"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if member == ():
			member = ctx.author
		else:
			member = member[0]
		await ctx.send(f"Kisses {member.mention} <3")

	@commands.command(help="Pokes someone")
	async def poke(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "poke"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if member == ():
			member = ctx.author
		else:
			member = member[0]
		await ctx.send(f"Pokes {member.mention}")

	@commands.command(help="Snuggles someone UwU")
	async def snuggle(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "snuggle"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if member == ():
			member = ctx.author
		else:
			member = member[0]
		await ctx.send(f"Snuggles {member.mention} UwU")

	@commands.command(help="Licks someone OwO")
	async def lick(self, ctx, *member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "lick"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if member == ():
			member = ctx.author
		else:
			member = member[0]
		await ctx.send(f"Licks {member.mention} OwO")

	@commands.command(help="Love someone!")
	async def love(self, ctx, member: discord.Member):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "love"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		"""if member.id == ctx.author.id:
			await ctx.send("<:error:724683693104562297> | You can't love yourself :(")
			return"""
		await ctx.send(f"{ctx.author.mention} loves {member.mention} <3")

def setup(bot):
	bot.add_cog(Furry(bot))
