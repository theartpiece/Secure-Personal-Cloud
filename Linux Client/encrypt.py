import os
import sqlite3

def aes(file,key,iv):
	bash_command = 'openssl enc -aes-128-cbc -nosalt '
	end = " > "+ '\"'+str(file)+".enc" + '\"' 
	os.system(bash_command + " -K " + str(key) + " -iv " + str(iv)  +" -base64 " + " -in "+ '\"'+ str(file) + '\"'+ end)
	# print(bash_command + " -K " + str(key) + " -iv " + str(iv) + " -base64 " + " -in "+ str(file))# + end)

def des_ede3(file,key,iv):
	bash_command = 'openssl enc -des-ede3-cbc -nosalt '
	end = " > "+ "\'"+str(file)+".enc" + "\'" 
	# end = " | tr -d \'\\n\' " 
	os.system(bash_command + " -K " + str(key) + " -iv " + str(iv) + " -base64 " + " -in "+"\'"+ str(file)+ "\'"+ end)
def des(file,key,iv):
	bash_command = 'openssl enc -des-cbc -nosalt '
	# end = " | tr -d \'\\n\' " 
	end = " > "+ "\'"+str(file)+".enc" + "\'" 
	os.system(bash_command + " -K " + str(key) + " -iv " + str(iv) + " -base64 " + " -in "+"\'"+ str(file) +"\'"+ end)

def dec_aes(file,key,iv):
	bash_command = 'openssl enc -aes-128-cbc -d -nosalt '
	end = " > "+ '\"'+ str(file[:-4]) + '\"'
	os.system(bash_command + " -K " + str(key) + " -iv " + str(iv)  +" -base64 " + " -in "+ '\"'+ str(file) + '\"' + end)
	 

def dec_des(file,key,iv):
	bash_command = 'openssl enc -des-cbc -d -nosalt '
	end = " > "+ "\'"+str(file[:-4]) +"\'"
	os.system(bash_command + " -K " + str(key) + " -iv " + str(iv)  +" -base64 " + " -in "+"\'"+ str(file)+ "\'"+ end)
	 

def dec_des_ede3(file,key,iv):
	bash_command = 'openssl enc -des-ede3-cbc -d -nosalt '
	end = " > "+ "\'"+str(file[:-4]) +"\'"  
	os.system(bash_command + " -K " + str(key) + " -iv " + str(iv)  +" -base64 " + " -in "+'\"'+ str(file) + '\"'+end)
	 
def extract_key():
	import os
	import sqlite3
	if not os.path.isfile("Files.db"): 
		print('  Do "SPC init" first')
		return 
	mydb = sqlite3.connect("Files.db")
	cur = mydb.cursor()
	cur.execute('''SELECT * FROM Schema''')
	dic={}
	for row in cur:
	    dic={'key':row[2], 'iv':row[1] , 'enc':row[0]}
	mydb.close()
	return dic
	


def choose_schema():
	import os
	if not os.path.isfile("Files.db"): 
		print('  Do "SPC init" first')
		return 
	mydb = sqlite3.connect("Files.db")
	cur = mydb.cursor()
	print("Choose an encryption schema:")
	print("1 AES")
	print("2 DES")
	print("3 DES-EDE3")
	choice = input()
	enc=''

	while True:
		if int(choice) == 1:
			specific = "-aes-128-cbc"
			enc='AES'
			break
		elif int(choice) == 2:
			specific = "-des-cbc"
			enc='DES'
			break
		elif int(choice) == 3:
			specific = "-des-ede3-cbc"
			enc='DES-EDE3'
			break
		else:
			print("Invalid Choice")

	bash_command = ' openssl enc -nosalt -base64 -P ' + specific + ' > .metadata'
	os.system(bash_command)
	with open('.metadata','r') as rfile:
		l1 = rfile.readline()
		l2 = rfile.readline()
		key = l1.strip().strip('key=')
		iv = l2.strip().strip('iv =')
		# print(enc,iv,key)
		cur.execute('''DELETE FROM Schema''')
		cur.execute("INSERT INTO Schema VALUES (?,?,?)",(enc,iv,key))
		cur.execute("Select * From Schema")
		for row in cur:
			print(row)
	os.remove('.metadata')
	mydb.commit()

		
def change_schema():
	choose_schema()

def encrypt_file(file):
	adict = extract_key()
	enc = adict['enc']
	key = adict['key']
	iv = adict['iv']
	# print(adict)
	if enc == 'AES':
		aes(file,key,iv)
	elif enc == 'DES':
		des(file,key,iv)
	elif enc == 'DES-EDE3':
		des_ede3(file,key,iv) 
	else:
		print("error in dump file")

def decrypt_file(file):
	adict = extract_key()
	enc = adict['enc']
	key = adict['key']
	iv = adict['iv']
	if enc == 'AES':
		dec_aes(file,key,iv)
	elif enc == 'DES':
		dec_des(file,key,iv)
	elif enc == 'DES-EDE3':
		dec_des_ede3(file,key,iv) 
	else:
		print("error in dump file")

def main():
	pass


if __name__ == '__main__':
	main()