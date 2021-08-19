import os
import os.path as osp
import hashlib
import sqlite3
import sys
import requests
import getpass





URL1 = 'http://127.0.0.1:8000/accounts/login/'
client = requests.session()

# Retrieve the CSRF token first
client.get(URL1)  # sets cookie
if 'csrftoken' in client.cookies:
    # Django 1.6 and up
    csrftoken = client.cookies['csrftoken']

login_data = dict(username=input('Username: '), password=getpass.getpass(), csrfmiddlewaretoken=csrftoken, next='/')
r1 = client.post(URL1, data=login_data, headers=dict(Referer=URL1))




URL = 'http://127.0.0.1:8000/user/upload/'
#client = requests.session()

# Retrieve the CSRF token first
client.get(URL)  # sets cookie
if 'csrftoken' in client.cookies:
    # Django 1.6 and up
    csrftoken = client.cookies['csrftoken']

#login_data = dict(username=input('Username: '), password=getpass.getpass(), csrfmiddlewaretoken=csrftoken, next='/')
#r = client.post(URL, data=login_data, headers=dict(Referer=URL))

# --- helpers ---

def write(text):
    """ helper for writing output, as a single point for replacement """
    print(text)

def filehash(filepath):
    blocksize = 64*1024
    sha = hashlib.sha256()
    with open(filepath, 'rb') as fp:
        while True:
            data = fp.read(blocksize)
            if not data:
                break
            sha.update(data)
    return sha.hexdigest() 

ROOT = '.'
for root, dirs, files in os.walk(ROOT):
    #print(dirs)
    #mydb = sqlite3.connect("ipl.db")
    #cur = mydb.cursor()
    # print(root)
    for fpath in [osp.join(root, f) for f in files]:
        # print(fpath)
        # size = osp.getsize(fpath)
        sha = filehash(fpath)
        name = osp.relpath(fpath, ROOT)
        myfiles = dict(docfile = open(fpath,'rb'))
        data_dict = dict(path = name, sha256 = sha, csrfmiddlewaretoken=csrftoken, next='/')
        r = client.post(URL,files = myfiles, data=data_dict, headers=dict(Referer=URL))
        print (sha, name)



