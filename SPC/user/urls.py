from django.contrib import admin

from django.conf.urls import url
from . import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # path(r'upload/', user.views.upload_file, name='upload'),
    url('upload/', views.upload_file, name='upload'),
    # url('download/', views.download_file, name='download')
    # url(r'^(?P<user_id>[0-9]+)/upload/$', views.upload_file, name='upload')
]
