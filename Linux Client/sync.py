#! /usr/bin/python3

def sync():
	import requests
	import getpass
	import os, sys
	import hashlib
	import json
	import sqlite3
	import os.path as osp
	import base64
	import tqdm
	import time
	import logging
	import signal
	try:
		def signal_handler(sig, frame):
		        print('You pressed Ctrl+C!')
		        sys.exit(0)
		signal.signal(signal.SIGINT, signal_handler)

		server_ip='http://127.0.0.1:8000/'
		observing_root='./'
		username=None
		password=None
		    
		def filehash(filepath):
		    file = open(filepath,'rb')
		    docfile=file.read()
		    docfile=base64.encodestring(docfile)
		    sha = hashlib.sha256()
		    sha.update(docfile)
		    sha=sha.hexdigest()
		    return sha

		def assure_path_exists(path):
		        dir = os.path.dirname(path)
		        if not os.path.exists(dir):
		                os.makedirs(dir)

		mydb = sqlite3.connect("Files.db")
		cur = mydb.cursor()
		cur.execute('''SELECT * FROM Server_ip''')
		for row in cur:
		    print("Server_ip is set to "+row[0])
		    server_ip=row[0]
		

		cur.execute('''SELECT * FROM Root''')
		for row in cur:
		    print('Syncing "'+row[0] +'" directory')
		    observing_root=row[0]


		cur.execute('''SELECT * FROM User''')
		for row in cur:
		    username=row[0]
		    password=row[1]

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


		# URL_login = server_ip+'accounts/login/'
		URL_login = server_ip+'accounts/login/'
		client = requests.session()

		# Retrieve the CSRF token first
		client.get(URL_login)  # sets cookie
		if 'csrftoken' in client.cookies:
		    csrftoken = client.cookies['csrftoken']

		# login_data = dict(username=input('Username: '), password=getpass.getpass(), csrfmiddlewaretoken=csrftoken, next='/')
		login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next='')
		r = client.post(URL_login, data=login_data, headers=dict(Referer=URL_login))
		
		log=[]
		def detailurl(path):
		    return server_ip+'api/file/'+path+'/'

		def getlist(mode=0):
			r=client.get(server_ip+'api/listfile/',stream=True)
			a=r.json()
			if mode==0:
				for entry in a:
					if entry['isdir']:
						print(entry['path'])
					else:
						print( entry['sha256'],entry['path'])
			elif mode==1:
				ans={}
				for entry in a:
					ans[entry['path']]=[entry['sha256'],entry['isdir']]
				return ans

		def getdetail(path):
			log=[]
			try:
				r=client.get(detailurl(path))
				a=r.json()
			except:
				# 
				log.append('  (server error)'.ljust(30)+path)
				return log

			# print(a['path'],a['sha256'],a['isdir'])
			try:
				sha=None
				if not a['isdir']:
					data = bytes(a['docfile'], 'utf-8')
					sha = hashlib.sha256()
					sha.update(data)
					sha=sha.hexdigest()
					data = base64.decodestring(data)
					if sha==a['sha256']:
						assure_path_exists(observing_root+path)
						file = open(observing_root+path, 'wb')
						file.write(data)
						# print(a['path'],'(downloaded)')
						log.append(' (downloaded)'.ljust(30)+path)
					else:
						log.append(' (failed (hash mismatch))'.ljust(30)+path)
				else:
					assure_path_exists(observing_root+a['path'])
					# print(a['path'],'(checked)')
					log.append(' (checked)'.ljust(30)+path)
				stamp = os.path.getmtime(observing_root+path)
				cur.execute("INSERT INTO Files (filepath, sha256, stamp) VALUES (?,?,?)",[path,sha,str(stamp)])
			except:
				# print(path,'(internal error)')
				log.append(' (internal error)'.ljust(30)+path)
			return log


		def updatefile(path):
		    URL_update = detailurl(path)
		    log=[]
		    try:
			    if os.path.isfile(observing_root+path):
			        r=client.get(server_ip)
			        if 'csrftoken' in client.cookies:
			            csrftoken = client.cookies['csrftoken']
			        file = open(observing_root+path,'rb')
			        docfile=file.read()
			        docfile=base64.encodestring(docfile)
			        sha = hashlib.sha256()
			        sha.update(docfile)
			        sha=sha.hexdigest()
			        data = dict(path = path, owner='jatin',sha256 = sha, docfile= docfile,isdir=False, csrfmiddlewaretoken=csrftoken)
			        r = client.put(URL_update, data=data, headers={"Referer": server_ip,"X-CSRFToken" : csrftoken})
			        if r.status_code != 200:
			        	dic=r.text[38:51]
			        	if dic=='hash mismatch':
			        		log.append(' (failed (hash mismatch))'.ljust(30)+path)
			        	else:
			        		log.append(' (server error)'.ljust(30)+path)
			        else:
			        	log.append(' (updated)'.ljust(30)+path)
			        # print(r.status_code,sha, path)
			        # print(r.status_code)
			    else:
			        # print(path,'(file does not exist)')
			        log.append(' (file does not exist)'.ljust(30)+path)
			# except IOError:
			#     pass
		    except:
		    	log.append(' (internal error)'.ljust(30)+path)
		    return log


		def uploadfile(path):
			URL_create=server_ip + 'api/file/'
			log=[]
			try:
				client.get(server_ip)
				if 'csrftoken' in client.cookies:
					csrftoken = client.cookies['csrftoken']
				docfile=None
				sha256=None
				isdir=True
				if os.path.isfile(observing_root+path):
					file = open(observing_root+path,'rb')
					docfile=file.read()
					docfile=base64.encodestring(docfile)
					sha = hashlib.sha256()
					sha.update(docfile)
					isdir=False
					sha256=sha.hexdigest()
				elif os.path.isdir(observing_root+path):
					pass
				else:
					# print(path,'(file does not exist)')
					log.append(' (file does not exist)'.ljust(30)+path)

				data = dict(path = path, sha256 = sha256, docfile=docfile , isdir=isdir, csrfmiddlewaretoken=csrftoken,  next='')

				r = client.post(URL_create, data=data, headers=dict(Referer=server_ip))
				if r.status_code != 201:
					# print('(server error)')
					dic=r.text[38:51]
					if dic=='hash mismatch':
						log.append(' (failed (hash mismatch))'.ljust(30)+path)
					else:
						log.append(' (server error)'.ljust(30)+path)
				else:
					# print(path, '(uploaded)')
					log.append(' (uploaded)'.ljust(30)+path)
			except:
				# print(path, '(failed)')
				log.append(' (internal error)'.ljust(30)+path)
			return log

		
		def deletefile(path):	
		    URL_delete=detailurl(path)
		    log=[]
		    try:
			    r=client.get(server_ip)
			  
			    if 'csrftoken' in client.cookies:
			        csrftoken = client.cookies['csrftoken']

			    data = dict(path = path, csrfmiddlewaretoken=csrftoken,  next='')
			    r = client.delete(URL_delete, data=data, headers={"Referer": server_ip, "X-CSRFToken" : csrftoken})
			    if r.status_code==str(404):
			        # print(path,'(file does not exist on server)')
			        log.append(' (file does not exist on server) '.ljust(30)+path)
			    elif r.status_code!=202:
			        # print(path,'(deleted)')
			        log.append(' (deleted from server)'.ljust(30)+path)
			    # print(r.status_code)
		    except:
		    	log.append(' (server error)'.ljust(30)+path)
		    return log


		client.get(server_ip) # if 'csrftoken' in client.cookies:
		csrftoken = client.cookies['csrftoken']
		URL_start_sync = server_ip+'api/begin/'#server_ip + 'api/begin/'
		f = client.post(URL_start_sync,dict(csrfmiddlewaretoken=csrftoken, id='linux-client', next='',headers=dict(Referer=server_ip)))
		g = f.json()


		if g['possible']=='True':


			dict_of_lcfiles={}
			dict_of_rmfiles={}

			cur.execute('''SELECT * FROM Files''')
			for row in cur:
				dict_of_lcfiles[row[0]]=row[1]
			list_of_lcfiles=dict_of_lcfiles.keys()
			dict_of_rmfiles=getlist(1)
			list_of_rmfiles=dict_of_rmfiles.keys()

			no_of_files=0
			for file in list_of_lcfiles:
				if file not in list_of_rmfiles:
					if os.path.isfile(observing_root+file):
						no_of_files+=1

			for file in list_of_rmfiles:
				if file not in list_of_lcfiles:
					if not dict_of_rmfiles[file][1]:
						# print(file,dict_of_rmfiles[file][1])
						no_of_files+=1

			for file in list_of_lcfiles:
				if file in list_of_rmfiles:
					if os.path.isfile(observing_root+file):
						no_of_files+=1




			pbar = tqdm.tqdm(total=no_of_files,ncols=100,mininterval=0,miniters=0,file=sys.stdout)

			for file in list_of_lcfiles:
				if file not in list_of_rmfiles:
					result=uploadfile(file)
					if os.path.isfile(observing_root+file):
						pbar.set_description(file.ljust(30))
						pbar.refresh()
						pbar.update(1)
						pbar.write(result[0])

			for file in list_of_rmfiles:
				if file not in list_of_lcfiles:
					result=getdetail(file)
					if not dict_of_rmfiles[file][1]:
						pbar.set_description(file.ljust(30))
						pbar.refresh()
						pbar.update(1)
						pbar.write(result[0])


			for file in list_of_lcfiles:
				if file in list_of_rmfiles:
					result=[]
					if dict_of_rmfiles[file][0]==dict_of_lcfiles[file]:
						# print(file.ljust(50),' (up to date)')
						result.append(' (up to date)'.ljust(30)+file)
					else:
						while True:
							# pbar.close()

							pbar.write('For "'+file+'", press "r" to keep remote copy or "l" for local copy')
							pbar.clear()
							choice=input()
							# pbar.clear()
							if choice=='r':
								result=getdetail(file)
								break
							elif choice=='l':
								result=updatefile(file)
								break
							else:
								pbar.write('Invalid choice!')
					if os.path.isfile(observing_root+file):
						pbar.set_description(file.ljust(30))
						pbar.refresh()
						pbar.update(1)
						pbar.write(result[0])
			pbar.close()




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
					# print(' (deleting)'.ljust(15),file)

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
					# print(' (adding)'.ljust(15),file)

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
					# print(' (updating)'.ljust(15),file)

			
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
	except:
		print('Sync failed')
		print('  Try after some time')


if __name__ == '__main__':
    sync()
    