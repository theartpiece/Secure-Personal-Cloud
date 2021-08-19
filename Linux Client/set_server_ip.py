def set(addr):
	import sqlite3
	import os
	if not os.path.isfile("Files.db"): 
		print('  Do "SPC init" first')
		return 
	mydb = sqlite3.connect("Files.db")
	cur = mydb.cursor()
	if addr[-1]!='/':
		addr=addr+'/'
	cur.execute('''DELETE FROM Server_ip''')
	cur.execute("INSERT INTO Server_ip (server_ip) VALUES ('"+addr+"')")
	cur.execute('''SELECT * FROM Server_ip''')
	for row in cur:
	    print("  Server_ip is set to "+row[0])
	mydb.commit()
	mydb.close()

def show():
	import sqlite3
	import os
	if not os.path.isfile("Files.db"): 
		print('  Do "SPC init" first')
		return 
	mydb = sqlite3.connect("Files.db")
	cur = mydb.cursor()
	cur.execute('''SELECT * FROM Server_ip''')
	row = cur.fetchone()
	if row==None:
		print("  Server url is not set")
		print('  Do "SPC server set <address>" first')
	else:
		cur.execute('''SELECT * FROM Server_ip''')
		for row in cur:
			port=row[0].split(':')[-1][0:-1]
			ip=':'.join(row[0].split(':')[0:-1])
			print('  Server ip is set to "'+ip+'"')
			print('  Server port is set to "'+port+'"')
	mydb.close()


