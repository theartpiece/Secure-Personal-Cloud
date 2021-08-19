#! /usr/bin/python3
    
def lsync():
	import getpass
	import os, sys
	import hashlib
	import sqlite3
	import os.path as osp
	import base64
	from encrypt import encrypt_file 
	try:
		def filehash(filepath):
			encrypt_file(filepath)
			file = open(filepath+'.enc','rb')
			docfile=file.read()
			sha = hashlib.sha256()
			sha.update(docfile)
			sha256=sha.hexdigest()
			os.remove(filepath+'.enc')
			return sha256


		mydb = sqlite3.connect("Files.db")
		cur = mydb.cursor()
		nothing=1
		cur.execute('''SELECT * FROM Root''')
		for row in cur:
		    print('Syncing "'+row[0] +'" directory locally')
		    print('  ','(use "SPC sync" to sync remotely)')
		    observing_root=row[0]


		list_of_files=[]
		list_of_dbfiles=[]

		for root, dirs, files in os.walk(observing_root):
			for fpath in [osp.join(root, f) for f in files]:
				name = osp.relpath(fpath, observing_root)
				list_of_files.append(name)

			for fpath in [osp.join(root, f) for f in dirs]:
				name = osp.relpath(fpath, observing_root)+'/'
				list_of_files.append(name)

		cur.execute('''SELECT * FROM Files''')
		for row in cur:
			list_of_dbfiles.append(row[0])


		for file in list_of_dbfiles:
			if file not in list_of_files:
				nothing=0
				cur.execute('''DELETE FROM Files WHERE filepath="'''+file+'"')
				print(' (deleting)'.ljust(15),file)

		for file in list_of_files:
			if file not in list_of_dbfiles:
				nothing=0
				if os.path.isdir(observing_root+file):
					sha256 = None
				else:
					sha256 = filehash(observing_root+file)
					      ##### check
				stamp = os.path.getmtime(observing_root+file)
				cur.execute("INSERT INTO Files (filepath, sha256, stamp) VALUES (?,?,?)",[file,sha256,str(stamp)])
				print(' (adding)'.ljust(15),file)

		for file in list_of_files:
			if file in list_of_dbfiles:
				stamp = os.path.getmtime(observing_root+file)
				cur.execute('''SELECT * FROM Files WHERE filepath="'''+ str(file) +'"')
				dbstamp=None
				for row in cur:
					dbstamp=row[2]
				stamp=float(stamp)
				dbstamp=float(dbstamp)
				if dbstamp<stamp:
					nothing=0
					sha256=None
					if not os.path.isdir(observing_root+file):
						sha256 = filehash(observing_root+file)
					if sha256==None:
						cur.execute("UPDATE Files SET stamp='"+str(stamp)+"' , sha256=NULL WHERE filepath='"+str(file)+"'")  
					else:
						cur.execute("UPDATE Files SET stamp='"+str(stamp)+"' , sha256='"+sha256+"' WHERE filepath='"+str(file)+"'")
					print(' (updating)'.ljust(15),file)
					# else:
					# 	print(file +' (no need to update database)')

		if nothing==1:
			print('Nothing to sync\n   (no changes made after last "SPC add)"')
		mydb.commit()
		mydb.close()
		return 1 
	except:
		print('Request failed')
		return 0

if __name__ == '__main__':
    lsync()