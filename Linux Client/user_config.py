def edit():
	import sqlite3
	import getpass
	import os
	if not os.path.isfile("Files.db"): 
		print('  Do "SPC init" first')
		return 
	mydb = sqlite3.connect("Files.db")
	cur = mydb.cursor()

	username=input("  Username: ")
	while True:
	    password=getpass.getpass("  Password: ")
	    confirmpassword=getpass.getpass("  Confirm Password: ")
	    if confirmpassword==password:
	        break

	cur.execute('''DELETE FROM User''')
	cur.execute("INSERT INTO User  VALUES (?, ?)", (username,password))
	print('  Authentication details set')
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
	cur.execute('''SELECT * FROM User''')
	row = cur.fetchone()
	if row==None:
		print("  Authentication details are not set")
		print('  Do "SPC config edit" first')
	else:
		cur.execute('''SELECT * FROM User''')
		for row in cur:
			dec=input('Confirm print authentication details ( "y" / "n" ): ')
			if dec=='y':
				print('  Username: '+row[0])
				print('  Password: '+row[1])
	mydb.close()
