import sqlite3, os

BlacklistDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}Blacklist.db")
BlacklistCursor = BlacklistDB.cursor()

def CheckBlacklist(UserID: int):
	BlacklistCursor.execute("SELECT Reason FROM blacklist WHERE UserID = ?",(UserID,))
	Blacklist = BlacklistCursor.fetchone()
	if Blacklist != None:
		return Blacklist[0]
	return False
