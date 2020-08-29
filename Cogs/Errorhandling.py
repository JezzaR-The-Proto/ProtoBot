import discord, time, math, sqlite3
from discord.ext import commands
from humanfriendly import format_timespan

class ErrorHandling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):

		if hasattr(ctx.command, 'on_error'):
			return

		ignored = (commands.CommandNotFound)

		error = getattr(error, 'original', error)

		if isinstance(error, ignored):
			return

		elif isinstance(error, commands.DisabledCommand):
			return await ctx.send(f'<:error:724683693104562297> | {ctx.command} has been disabled.')

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				return await ctx.author.send(f'<:error:724683693104562297> | {ctx.command} can not be used in Private Messages.')
			except:
				pass

		elif isinstance(error, commands.errors.MissingRequiredArgument):
			return await ctx.send(f"<:error:724683693104562297> | {error.args[0].capitalize()}")

		elif isinstance(error, commands.MissingPermissions):
			return await ctx.send(f"<:error:724683693104562297> | You do not have permissions for this action! You need the permission {error.missing_perms[0]}")

		elif isinstance(error, discord.errors.Forbidden):
			return await ctx.send("<:error:724683693104562297> | I am missing permissions to do this!")

		elif isinstance(error, commands.errors.NotOwner):
			return await ctx.send("<:error:724683693104562297> | You are not the bot owner, you aren't supposed to know about this command!")

		elif isinstance(error, commands.errors.BadArgument):
			return await ctx.send("<:error:724683693104562297> | You have sent a bad argument.")

		elif isinstance(error, commands.CommandOnCooldown):
			seconds = math.ceil(error.retry_after)
			towait = format_timespan(seconds)
			return await ctx.send(f"<:error:724683693104562297> | You need to wait {towait} to do this command again.")

		elif isinstance(error, sqlite3.OperationalError):
			return await ctx.send(f"<:error:724683693104562297> | There was a database error. The error message is `{error.capitalize()}`")

		elif isinstance(error, commands.errors.ExtensionNotFound):
			return await ctx.send(f"<:error:724683693104562297> | That extension was not found.")

		else:
			with open("Error.log", "a") as ErrorFile:
				ErrorFile.write(f"Error type: {type(error)}, Error message: {error}")
			return await ctx.send("<:error:724683693104562297> | An error has occured but has not been handled. Check the console for output.")

def setup(bot):
	bot.add_cog(ErrorHandling(bot))
