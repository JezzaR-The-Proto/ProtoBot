import discord, datetime, typing
from discord.ext import commands
from CheckBlacklist import CheckBlacklist

class Help(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.IgnoreCogs = ["ErrorHandling","Listeners","Help"]
		bot.remove_command("help")

	@commands.command(help="Display help command.")
	async def help(self, ctx, Cog: typing.Optional[str] = None):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if Cog == None:
			HelpEmbed = discord.Embed(title="ProtoBot modules help", timestamp=datetime.datetime.utcnow())
			Cogs = self.bot.cogs.values()
			for Cog in Cogs:
				if Cog.qualified_name in self.IgnoreCogs:
					continue
				if len(Cog.get_commands()) < 1:
					continue
				HelpEmbed.add_field(name=Cog.qualified_name, value=f"{len(Cog.get_commands())} commands")
			HelpEmbed.set_footer(text=f"Use {ctx.prefix}help (module) for more help")
		else:
			Cogs = self.bot.cogs.values()
			Cog = Cog.capitalize()
			CogFound = None
			for CogValue in Cogs:
				if Cog == CogValue.qualified_name:
					CogFound = CogValue
			if CogFound == None:
				await ctx.send(f"Module {Cog} does not exist.")
				return
			HelpEmbed = discord.Embed(title=f"ProtoBot help for `{Cog}` module", timestamp=datetime.datetime.utcnow())
			for Command in CogFound.get_commands():
				HelpEmbed.add_field(name=Command.name, value=Command.help)
			HelpEmbed.set_footer(text=f"Use {ctx.prefix}help to see all modules")
		await ctx.send("",embed=HelpEmbed)

def setup(bot):
	bot.add_cog(Help(bot))
