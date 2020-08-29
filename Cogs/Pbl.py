import discord, sqlite3, typing, requests, os
from discord.ext import commands
from CheckDisabled import CheckDisabled
from CheckBlacklist import CheckBlacklist
from ParsePBL import Parse, GetData

class Pbl(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.PBLDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}PBL.db")
		self.PBLCursor = self.PBLDB.cursor()

	@commands.command(help="Shows PBL help.")
	async def pblhelp(self, ctx):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "pblhelp"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		PBLEmbed = discord.Embed(title="PBL Help")
		PBLEmbed.add_field(name="What is PBL?", value="PBL is a simple programming language made by JezzaProto#6483 to allow people to run simple code on messages safely.\nIt was made specifically for this bot.")
		PBLEmbed.add_field(name="How can I remove my PBLs?", value="You can remove a PBL by its name. If you run the command `p+pbl remove {name}` you can remove that command if it exists.", inline=False)
		PBLEmbed.add_field(name="What can I do with PBL?", value="If you make a .pbl file and send it with the command `p+pbl add {name}` you can add a pbl script to your scripts.")
		PBLEmbed.add_field(name="How can I run my code?", value="You can run your PBL file by using `p+pbl run {name} {message}` and the PBL file will run on the message. You must have added your script to the bot for this to work.")
		PBLEmbed.add_field(name="How do I make a .pbl file?", value="It's very simple. All you have to do is create a file with the .pbl extension, then in a text editor, add operands and opcodes that PBL recognises.")
		PBLEmbed.add_field(name="RPL Opcode", value="RPL (Replace) is used along with 2 operands. Ut replaces the first operand with the second.", inline=False)
		PBLEmbed.add_field(name="DEL Opcode", value="DEL (Delete) is used along with 1 operand. It removes all occurances of this operand in the message.")
		await ctx.send("",embed=PBLEmbed)

	@commands.command(help="The main PBL command.\nUse as `pbl add {name}` or `pbl run {name} {message}`")
	async def pbl(self, ctx, Mode: str, Name: str, *Message):
		if CheckBlacklist(ctx.author.id):
			await ctx.author.send(f"You have been banned from using ProtoBot for reason {CheckBlacklist(ctx.author.id)}")
			return
		if CheckDisabled(ctx.guild.id, "pbl"):
			await ctx.send("<:error:724683693104562297> | This command has been disabled for this server.", delete_after=15)
			return
		if Mode.lower() == "add":
			ValidFileFound = False
			for Attachment in ctx.message.attachments:
				if Attachment.filename.split(".")[-1] == "pbl":
					ValidFileFound = True
					FileURL = Attachment.url
					break
				else:
					continue
			if not ValidFileFound:
				await ctx.send("<:error:724683693104562297> | You have not sent a valid PBL file.")
				return
			FileReq = requests.get(FileURL)
			with open(f"{str(ctx.author.id)}.pbl","wb") as File:
				if len(FileReq.content) > 102400:
					await ctx.send("<:error:724683693104562297> | This file is too big.")
					return
				File.write(FileReq.content)
			self.PBLCursor.execute("SELECT * FROM pbl WHERE UserID = ?",(ctx.author.id,))
			CurrentPBLs = self.PBLCursor.fetchone()
			if CurrentPBLs == None:
				Data = GetData(f"{ctx.author.id}.pbl")
				if Data == False:
					await ctx.send("<:error:724683693104562297> | Something failed parsing the file.")
					return
				Data = "\uFEFF".join(Data)
				self.PBLCursor.execute("INSERT INTO pbl(UserID, PBL1, PBL2, PBL3, PBL4, PBL5) VALUES(?,?,?,?,?,?)",(ctx.author.id, f"{Name}\uFEFF{Data}", None, None, None, None))
			else:
				count = 1
				CurrentPBLs = CurrentPBLs[1:]
				for PBL in CurrentPBLs:
					if PBL == None:
						break
					if PBL.split("\uFEFF")[0].lower() == Name.lower():
						await ctx.send("<:error:724683693104562297> | You already have a PBL with this name.")
						return
					count += 1
				Data = GetData(f"{ctx.author.id}.pbl")
				if Data == False:
					await ctx.send("<:error:724683693104562297> | Something failed parsing the file.")
					return
				Data = "\uFEFF".join(Data)
				self.PBLCursor.execute(f"UPDATE pbl SET PBL{count} = ? WHERE UserID = ?",(f"{Name}\uFEFF{Data}", ctx.author.id))
			self.PBLDB.commit()
			os.remove(f"{ctx.author.id}.pbl")
			await ctx.send(f"Added PBL file to db as `{Name}`.")
		elif Mode.lower() == "run":
			if Message == ():
				await ctx.send("<:error:724683693104562297> | You must specify a message to use this PBL with.")
				return
			Message = " ".join(Message)
			self.PBLCursor.execute("SELECT * FROM pbl WHERE UserID = ?",(ctx.author.id,))
			CurrentPBLs = self.PBLCursor.fetchone()
			CurrentPBLs = CurrentPBLs[1:]
			CorrectPBL = None
			for PBL in CurrentPBLs:
				if PBL.split("\uFEFF")[0].lower() == Name.lower():
					CorrectPBL = PBL.split("\uFEFF")[1:]
					break
			if CorrectPBL == None:
				await ctx.send("<:error:724683693104562297> | You have no PBL with this name.")
				return
			Msg = Parse(CorrectPBL, Message)
			await ctx.send(f"New message: `{Msg}`")
		elif Mode.lower() == "remove":
			self.PBLCursor.execute("SELECT * FROM pbl WHERE UserID = ?",(ctx.author.id,))
			CurrentPBLs = self.PBLCursor.fetchone()
			if CurrentPBLs == None:
				await ctx.send("<:error:724683693104562297> | You do not have any PBLs.")
				return
			CurrentPBLs = CurrentPBLs[1:]
			CorrectPBL = None
			count = 1
			for PBL in CurrentPBLs:
				if PBL == None:
					count += 1
					continue
				if PBL.split("\uFEFF")[0].lower() == Name.lower():
					CorrectPBL = PBL.split("\uFEFF")[1:]
					break
				count += 1
			if CorrectPBL == None:
				await ctx.send("<:error:724683693104562297> | You have no PBL with this name.")
				return
			self.PBLCursor.execute(f"UPDATE pbl SET PBL{count} = ? WHERE UserID = ?",(None, ctx.author.id))
			self.PBLDB.commit()
			await ctx.send(f"PBL {Name} has been removed from your PBLs.")


def setup(bot):
	bot.add_cog(Pbl(bot))
