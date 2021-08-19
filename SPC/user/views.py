from django import db
from django.http import HttpResponseRedirect, HttpResponse
# from django.shortcuts import render
# from django.template.context_processors import csrf
# from django.views.decorators.csrf import csrf_exempt
from .forms import FileUploadForm, FileDownloadForm
from .models import File
from django.shortcuts import render_to_response, render,redirect,get_object_or_404
import socket
# from django.template import RequestContext
# from django.urls import reverse


def upload_file(request):
    # user_id):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            newfile = File()
            newfile.owner = request.user
            newfile.sha256 = form.cleaned_data['sha256']
            newfile.path = form.cleaned_data['path']
            temp = request.POST.get('docfile', False)
            if isinstance(temp, str):
                temp = temp.encode('utf-8')
                newfile.docfile = temp
            else:
                newfile.docfile = request.FILES['docfile'].read()
            try:
                newfile.save()
            except db.utils.IntegrityError:
                File.objects.filter(owner=request.user, path=form.cleaned_data['path']).\
                    update(sha256=form.cleaned_data['sha256'], docfile=request.FILES['docfile'].read())

            return redirect('home')
        else:
            return HttpResponse("<h1>Form Invalid</h1> ")
    else:
        form = FileUploadForm()  # A empty, unbound form
        return render(request, 'user/list.html', {'form': form})


# def download_file(request):
#     if request.method == 'POST':
#         form = FileDownloadForm(request.POST, request.FILES)
#         if form.is_valid():
#             owner = request.user
#             port = 8010  # Reserve a port for your service every new transfer wants a new port or you must wait.
#             s = socket.socket()  # Create a socket object
#             host = ""  # Get local machine name
#             s.bind((host, port))  # Bind to the port
#             s.listen(5)  # Now wait for client connection.
#
#             hostname = socket.gethostname()
#             IPAddr = socket.gethostbyname(hostname)
#             print("Your Computer Name is:" + hostname)
#             print("Your Computer IP Address is:" + IPAddr)
#
#             print('Server listening....')
#
#             while True:
#                 conn, addr = s.accept()  # Establish connection with client.
#                 print('Got connection from', addr)
#                 data = conn.recv(1024)
#                 print('Server received', repr(data))
#
#                 filename = 'db.sqlite3'  # In the same folder or path is this file running must the file you want to tranfser to be
#                 f = open(filename, 'rb')
#                 l = f.read(1024)
#                 while (l):
#                     conn.send(l)
#                     print('Sent ', repr(l))
#                     l = f.read(1024)
#                 f.close()
#
#                 print('Done sending')
#                 conn.send('Thank you for connecting')
#                 conn.close()
#
#             return redirect('home')
#         else:
#             return HttpResponse("<h1>Form Invalid</h1> ")
#     else:
#         form = FileDownloadForm()  # A empty, unbound form
#         return render(request, 'user/path.html', {'form': form})


