def set(path):
	import sqlite3
	import os
	if not os.path.isfile("Files.db"): 
		print('  Do "SPC init" first')
		return 
	mydb = sqlite3.connect("Files.db")
	cur = mydb.cursor()

	root=path
	if root[-1]!='/':
		root=root+'/'
	if not os.path.isdir(root): 
		print(' "',root,'"does not exist!')
		print('  (enter existing directory)')
		return
	else:
		print('Observing "'+root+'"')
	
	cur.execute("INSERT INTO Root (root) VALUES ('"+root+"')")
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
	cur.execute('''SELECT * FROM Root''')
	if not cur:
		print("  Observing root is not set")
		print('  Do "SPC observe <path>" first')
	for row in cur:
		print('Observing "'+row[0]+'"')
	mydb.close()
