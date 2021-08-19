def initialise():
	import sqlite3
	import getpass
	import os
	if os.path.isfile("Files.db"): 
		os.remove("Files.db")
	mydb = sqlite3.connect("Files.db")
	cur = mydb.cursor()

	dschema='AES'
	div='90D906A1090B9D50BEFDCEF7FC520FC0'
	dkey='C30F3CFD3A437F9CF605C4A887F97D40'

	cur.execute('''CREATE TABLE Files (filepath varchar(200) Primary key,
	sha256 varchar(64), stamp timestamp)''')
	cur.execute('''CREATE TABLE User (name varchar(200) Primary key,password varchar(200))''')
	cur.execute('''CREATE TABLE Root (root varchar(200))''')
	cur.execute('''CREATE TABLE Server_ip (server_ip varchar(200))''')
	cur.execute('''CREATE TABLE Schema (schema varchar(100), iv varchar(100), key varchar(100))''')

	cur.execute("INSERT INTO Server_ip (server_ip) VALUES ('http://127.0.0.1:8000/')")
	cur.execute("INSERT INTO Schema VALUES (?,?,?) ",(dschema,div,dkey))

	# cur.execute('''SELECT * FROM User''')
	# for row in cur:
	#     print(row)
	mydb.commit()
	mydb.close()
