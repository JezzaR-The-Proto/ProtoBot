import sqlite3
con = sqlite3.connect("Currency.db")
cur = con.cursor()
cur.execute("SELECT ProtoPoints FROM protopoints WHERE UserID = 112633269010300928")
credits = cur.fetchone()
print(credits)
print(credits[0])
