def update():
	from rsync import sync
	from lsync import lsync
	from encrypt import change_schema,encrypt_file
	import requests
	import getpass
	import os, sys
	import hashlib
	import json
	import sqlite3
	import os.path as osp
	import tqdm
	import time
	import logging
	import signal
	print('Adding all changes since last "SPC add"')
	print()
	if not lsync():
		print('Failed adding all files')
		return 
	print()
	print('Syncing all changes since last "SPC sync"')
	if not sync():
		print('Failed syncing with server')
		return 
	print()
	change_schema()
	print()
	print('Updating user data on server')
	# try:
	def signal_handler(sig, frame):
	        print('You pressed Ctrl+C!')
	        sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)

	server_ip='http://127.0.0.1:8000/'
	observing_root=None
	username=None
	password=None
	lcschema=None
	    
	def assure_path_exists(path):
		dir = os.path.dirname(path)
		if not os.path.exists(dir):
			os.makedirs(dir)

	mydb = sqlite3.connect("Files.db")
	cur = mydb.cursor()
	cur.execute('''SELECT * FROM Server_ip''')
	for row in cur:
	    # print("Server_ip is set to "+row[0])
	    server_ip=row[0]
	

	cur.execute('''SELECT * FROM Root''')
	for row in cur:
	    # print('Syncing "'+row[0] +'" directory')
	    observing_root=row[0]


	cur.execute('''SELECT * FROM User''')
	for row in cur:
	    username=row[0]
	    password=row[1]

	cur.execute('''SELECT * FROM Schema''')
	for row in cur:
		print(row[0])
		lcschema=row[0]


	list_of_files=[]
	
	for root, dirs, files in os.walk(observing_root):
		for fpath in [osp.join(root, f) for f in files]:
			name = osp.relpath(fpath, observing_root)
			list_of_files.append(name)

		for fpath in [osp.join(root, f) for f in dirs]:
			name = osp.relpath(fpath, observing_root)+'/'
			list_of_files.append(name)

	cur.execute('''DELETE FROM Files''')
	
	# URL_login = server_ip+'accounts/login/'
	URL_login = server_ip+'api-auth/login/'
	client = requests.session()

	# Retrieve the CSRF token first
	client.get(URL_login)  # sets cookie
	if 'csrftoken' in client.cookies:
	    csrftoken = client.cookies['csrftoken']

	# login_data = dict(username=input('Username: '), password=getpass.getpass(), csrfmiddlewaretoken=csrftoken, next='/')
	login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next='')
	r = client.post(URL_login, data=login_data, headers=dict(Referer=URL_login))
	

	def detailurl(path):
	    return server_ip+'api/file/'+path+'/'


	def updatefile(path):
	    URL_update = detailurl(path)
	    log=[]
	    # try:
	    if os.path.isfile(observing_root+path):
	        r=client.get(server_ip)
	        if 'csrftoken' in client.cookies:
	            csrftoken = client.cookies['csrftoken']

	        encrypt_file(observing_root+path)
	        file = open(observing_root+path+'.enc','rb')
	        docfile=file.read()
	        sha = hashlib.sha256()
	        sha.update(docfile)
	        sha=sha.hexdigest()
	        data = dict(path = path, owner='jatin',sha256 = sha, docfile= docfile,isdir=False, schema=lcschema,csrfmiddlewaretoken=csrftoken)
	        os.remove(observing_root+path+'.enc')
	        r = client.put(URL_update, data=data, headers={"Referer": server_ip,"X-CSRFToken" : csrftoken})
	        if r.status_code != 200:
	        	dic=r.text[38:51]
	        	if dic=='hash mismatch':
	        		log.append(' (failed (hash mismatch))'.ljust(30)+path)
	        	else:
	        		log.append(' (server error)'.ljust(30)+path)
	        else:
	        	log.append(' (updated)'.ljust(30)+path)
	        stamp = os.path.getmtime(observing_root+path)
	        cur.execute("INSERT INTO Files (filepath, sha256, stamp) VALUES (?,?,?)",[path,sha,str(stamp)])
	    else:
	    	stamp = os.path.getmtime(observing_root+path)
	    	cur.execute("INSERT INTO Files (filepath, sha256, stamp) VALUES (?,?,?)",[path,None,str(stamp)])
	    	log.append(' (file does not exist)'.ljust(30)+path)
	    # except:
	    # 	log.append(' (internal error)'.ljust(30)+path)
	    return log

	client.get(server_ip) # if 'csrftoken' in client.cookies:
	csrftoken = client.cookies['csrftoken']
	URL_start_sync = server_ip+'api/begin/'#server_ip + 'api/begin/'
	f = client.post(URL_start_sync,dict(csrfmiddlewaretoken=csrftoken, id='linux-client', next='',headers=dict(Referer=server_ip)))
	g = f.json()


	if g['possible']=='True':

		no_of_files=0
		for file in list_of_files:
			if os.path.isfile(observing_root+file):
				no_of_files+=1

		pbar = tqdm.tqdm(total=no_of_files,ncols=100,mininterval=0,miniters=0,file=sys.stdout)

		for file in list_of_files:
			result=updatefile(file)
			if os.path.isfile(observing_root+file):
				pbar.set_description(file.ljust(30))
				pbar.refresh()
				pbar.update(1)
				pbar.write(result[0])
		pbar.close()

		mydb.commit()
		

		csrftoken = client.cookies['csrftoken']
		URL_end_sync = server_ip + 'api/end/'    # URL_start_sync = 'http://127.0.0.1:8000/api/begin/'#server_ip + 'api/begin/'
		sync_ender = client.post(URL_end_sync,dict(csrfmiddlewaretoken=csrftoken,id='linux-client', next='',headers=dict(Referer=server_ip)))
		# print(sync_ender.headers)
		h = sync_ender.json()  # client.post(URL_end_sync, headers=dict(Referer=URL_end_sync))
		if h['status']=='200':
			print('Sync completed')
		else:
			print('Some error occurred while executing sync')
			print('  Try after some time')

	else:
		print('Sync failed')
		print('  (either remote server is executing another sync request by this user or is in a deadlock)')
		print('  Try after some time')
	# except:
	# 	print('Failed updating schema')

def list():
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
	dec=input('Confirm print authentication details ( "y" / "n" ): ')
	if dec=='y':
		print('schema: '+dic['enc'])
		print('key: '+dic['key'])
		print('iv: '+dic['iv'])
	mydb.close()


def dump():
	import os
	import sqlite3
	import pickle
	if not os.path.isfile("Files.db"): 
		print('  Do "SPC init" first')
		return 
	mydb = sqlite3.connect("Files.db")
	cur = mydb.cursor()
	cur.execute('''SELECT * FROM Schema''')
	dic={}
	for row in cur:
	    dic={'key':row[2], 'iv':row[1] , 'schema':row[0]}
	with open('dumpfile.pickle', 'wb') as handle:
		pickle.dump(dic, handle, protocol=pickle.HIGHEST_PROTOCOL)
	mydb.close()


