#! /usr/bin/python3
import requests
import getpass
import os
import hashlib
import json
import base64

server_ip='http://10.196.21.97:8000/'
observing_root='./'

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

def main():
    # URL_login = server_ip+'accounts/login/'
    URL_login = server_ip+'api-auth/login/'
    client = requests.session()

    # Retrieve the CSRF token first
    client.get(URL_login)  # sets cookie
    if 'csrftoken' in client.cookies:
        csrftoken = client.cookies['csrftoken']

    # login_data = dict(username=input('Username: '), password=getpass.getpass(), csrfmiddlewaretoken=csrftoken, next='/')
    login_data = dict(username='jatin', password='jatin1234', csrfmiddlewaretoken=csrftoken, next='')
    r = client.post(URL_login, data=login_data, headers=dict(Referer=URL_login))
    # print(r.text)
    # print(r.headers)


    def getlist():
        r=client.get(server_ip+'api/listfile/')
        a=r.json()
        print(a)
        for entry in a:
            print(entry['path'])
        print()

    def getdetail(path):
        r=client.get(server_ip+'api/file/'+path)
        a=r.json()
        # print(r.text)
        print('sha256:  '+a['sha256'])
        # print('data:  '+a['docfile'])
        data = bytes(a['docfile'], 'utf-8')
        data = base64.decodestring(data)
        file = open(path, 'wb')
        file.write(data)
        print(r.status_code)

    def updatefile(path):
        URL_update = server_ip + 'api/file/'+path+'/'
        exists = os.path.isfile(observing_root+path)

        if exists:
            r=client.get(server_ip)
            if 'csrftoken' in client.cookies:
                csrftoken = client.cookies['csrftoken']
            sha = filehash(observing_root+path)
            data = dict(path = path, owner='jatin',sha256 = sha, docfile= open(observing_root+path,'rb') , csrfmiddlewaretoken=csrftoken)
            # print(data)
            r = client.put(URL_update, data=data, headers={"Referer": server_ip,"X-CSRFToken" : csrftoken})
            # print(r.text)
            if r.status_code == 500:
                print('This file already exists on the server, try updating instead or delete this first!')
            print(sha, path)
            print(r.status_code)
        else:
            print('File does not exist!')


    def uploadfile(path):
        URL_create=server_ip + 'api/file/'
        exists = os.path.isfile(observing_root+path)
        if exists:
            client.get(server_ip)
            if 'csrftoken' in client.cookies:
                csrftoken = client.cookies['csrftoken']
            # sha = filehash(observing_root+path)
            # print(sha)
            file = open(observing_root+path,'rb')
            docfile=file.read()
            docfile=base64.encodestring(docfile)
            blocksize = 64*1024
            sha = hashlib.sha256()
            sha.update(docfile)
            sha=sha.hexdigest()
            print(sha) 
            # data = dict(docfile = open(observing_root+path,'rb'))
            data = dict(path = path, sha256 = sha, docfile=docfile , csrfmiddlewaretoken=csrftoken,  next='')
            r = client.post(URL_create, data=data, headers=dict(Referer=server_ip))
            if r.status_code == 500:
                print('This file already exists on the server, try updating instead or delete this first!')
            print(r.status_code)
        else:
            print('File does not exist!')

    def deletefile(path):
        URL_delete=server_ip + 'api/file/'+path+'/'
        r=client.get(server_ip)
      
        if 'csrftoken' in client.cookies:
            csrftoken = client.cookies['csrftoken']
        # sha = filehash(observing_root+path)
        # file = open(observing_root+path,'rb')
        # docfile=file.read() 
        # data = dict(docfile = open(observing_root+path,'rb'))
        data = dict(path = path, csrfmiddlewaretoken=csrftoken,  next='')
        r = client.delete(URL_delete, data=data, headers={"Referer": server_ip, "X-CSRFToken" : csrftoken})
        if r.status_code == 404:
            print('This file does not exist on the server!')
        else:
            print('Successfully deleted '+path)
        print(r.status_code)


    while True:
        foo=input('Ready for duty: ')
        if foo == 'list':
            getlist()

        elif foo == 'detail':
            path = input('Input file path: ')
            getdetail(path)

        elif foo=='upload':
            path = input('Input file path: ')
            uploadfile(path)

        elif foo=='update':
            path = input('Input file path: ')
            updatefile(path)

        elif foo=='delete':
            path = input('Input file path: ')
            deletefile(path)

        else:
            print('Invalid Argument!')
            print("Type 'help' for help")



if __name__ == '__main__':
    main()


