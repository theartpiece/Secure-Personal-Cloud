#----> using basic
#
# from django.urls import path
# from django.urls import re_path
# from rest_framework.urlpatterns import format_suffix_patterns
# from . import views
# from rest_framework.schemas import get_schema_view
#
#
#
# schema_view = get_schema_view(title='Pastebin API')
#
# urlpatterns = [
#     re_path('schema/$', schema_view),
#     path(r'filelist/', views.FileList.as_view()),
#     path(r'fileupload/', views.FileUpload.as_view()),
#     re_path(r'^filedownload/(?P<path>.+)/', views.FileDownload.as_view()),
#     re_path(r'^fileupdate/(?P<path>.+)/', views.FileUpdate.as_view()),
#     # path(r'filedownload/()', views.FileDownload.as_view()),
# ]
#
# urlpatterns = format_suffix_patterns(urlpatterns)






#----> using viewsets
#
# from django.urls import re_path
# from rest_framework.urlpatterns import format_suffix_patterns
# from .views import FileViewSet
# from django.urls import path
#
#
# file_list = FileViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })
#
# file_detail = FileViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })
#
#
# urlpatterns = format_suffix_patterns([
#
#     path('file/', file_list, name='file-list'),
#     re_path('file/(?P<path>.+)$/', file_detail, name='file-detail'),
#
# ])
#

#----> using router
#
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework.schemas import get_schema_view

# schema_view = get_schema_view(title='Pastebin API')

router = DefaultRouter()
router.register(r'file', views.FileViewSet, basename='file')


urlpatterns = [
    # path('schema/', schema_view),
    path('listfile/',views.FileList.as_view(), name='listfile'),
    path('listfile.json/',views.FileListjson.as_view(), name='listfile.json'),
    path('', include(router.urls)),
    path('begin/',views.begin_sync, name='begin'),
    path('end/',views.end_sync, name='end')
]

