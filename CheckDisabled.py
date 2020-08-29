import sqlite3, os

SettingsDB = sqlite3.connect(f".{os.path.sep}Databases{os.path.sep}ServerSettings.db")
SettingsCursor = SettingsDB.cursor()

def CheckDisabled(GuildID: int, CommandName: str):
	SettingsCursor.execute("SELECT Disabled FROM disabledcommands WHERE GuildID = ?",(GuildID,))
	IsDisabled = SettingsCursor.fetchone()
	if IsDisabled == None:
		return False
	if IsDisabled[0] == "":
		return False
	IsDisabled = IsDisabled[0]
	IsDisabled = IsDisabled.split(",")
	for Command in IsDisabled:
		if Command.lower() == CommandName.lower():
			return True
	return False
