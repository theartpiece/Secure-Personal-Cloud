from django.contrib.auth.models import User

from django.http import HttpResponse
from rest_framework import generics
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
# from rest_framework.parsers import MultiPartParser, FormParser
# from django.db import transaction
from api.permissions import IsOwner
from user.models import File
from .serializers import FileSerializer, FileListSerializer
import datetime
from django.http import Http404
from django.http import JsonResponse

sync = []
timer = {}

# @transaction.Atomic


class FileViewSet(viewsets.ModelViewSet):
    # with transaction.atomic():
    lookup_field = 'path'
    lookup_value_regex = '.+'

    # sp = transaction.savepoint()

    serializer_class = FileSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    # @transaction.atomic
    def get_queryset(self):
        global timer
        # self.request. user = self.request.user#User.objects.select_for_update().get(id=self.request.user.id)
        now = datetime.datetime.now()
        timer[self.request.user] = now
        return File.objects.filter(owner=self.request.user)

    # @transaction.atomic
    def perform_create(self, serializer):
        now = datetime.datetime.now()
        timer[self.request.user] = now
        # print(self.request.data['path'])
        serializer.save(owner=self.request.user)

    global timer

    # queryset = File.objects.filter()

    # transaction.savepoint_rollback(sp)


class FileList(generics.ListAPIView):
    def get_queryset(self):
        # user = User.objects.select_for_update().get(id=self.request.user.id)
        return File.objects.filter(owner=self.request.user)

    serializer_class = FileListSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

class FileListjson(generics.ListAPIView):
    renderer_classes = [renderers.JSONRenderer]
    def get_queryset(self):
        # user = User.objects.select_for_update().get(id=self.request.user.id)
        return File.objects.filter(owner=self.request.user)

    serializer_class = FileListSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)


def begin_sync(request):
    if request.user.is_authenticated:
        if 'id' in request.POST.keys():
            global sync
            global timer
            use = request.user
            if use in sync:
                now = datetime.datetime.now()
                dif = now - timer[use]
                if dif.total_seconds() < 60:
                    js = {'possible': 'False'}
                    # timer[use], 'dif': dif.total_seconds(), 'now': now.second}
                    return JsonResponse(js)
                else:
                    now = datetime.datetime.now()
                    timer[use] = now
                    js = {'possible': 'True'}
                    return JsonResponse(js)
            else:
                sync.append(use)
                now = datetime.datetime.now()
                timer[use] = now
                # print(now)
                js = {'possible': 'True'}
                return JsonResponse(js)
        else:
            raise Http404('This URL is not meant for your use.')
    else:
        raise Http404('Unauthorized access')


def end_sync(request):
    if request.user.is_authenticated:
        global sync
        if 'id' in request.POST.keys():
            use = request.user
            sync.remove(use)
            return JsonResponse({'status': '200'})
        else:
            raise Http404('This URL is not meant for your use.')
    else:
        raise Http404('Unauthorized access')
