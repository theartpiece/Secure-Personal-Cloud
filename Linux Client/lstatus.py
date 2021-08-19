#! /usr/bin/python3



def lstatus():
	import os, sys
	import hashlib
	import sqlite3
	import os.path as osp
	import base64
	from encrypt import encrypt_file

	try:
		observing_root=None
		    
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

		cur.execute('''SELECT * FROM Root''')
		for row in cur:
		    observing_root=row[0]

		
		print('Changes made after last remote sync in "'+observing_root+'" directory:')
		print('  ','(use "SPC add" to update what will be synced remotely)')
		nothing=1
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
				cur.execute('''DELETE FROM Files WHERE filepath="'''+file+'"')
				nothing=0
				print(' (deleted)'.ljust(15),file)

		for file in list_of_files:
			if file not in list_of_dbfiles:
				nothing=0
				print(' (added)'.ljust(15),file)

		for file in list_of_files:
			if file in list_of_dbfiles:
				stamp = os.path.getmtime(observing_root+file)
				cur.execute('''SELECT * FROM Files WHERE filepath="'''+ file +'"')
				dbstamp=None
				for row in cur:
					dbstamp=row[2]
				stamp=float(stamp)
				dbstamp=float(dbstamp)
				if dbstamp<stamp:
					nothing=0     
					print(' (modified)'.ljust(15),file)

		if nothing==1:
			print('Nothing to show\n   (no changes made after last "SPC add)"')
		mydb.close()
	except:
		print('Request failed')


if __name__ == '__main__':
    lstatus()