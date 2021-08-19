import base64

from django.contrib.auth.models import User
from django.db import models

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<id>/<filename>
    return 'documents/{0}/{1}'.format(str(instance.owner)+ "/" + str(instance.path), filename)


# class FileManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(owner=request.user)


class File(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=1000)
    sha256 = models.CharField(max_length=1000, null=True, blank=True)
    docfile = models.BinaryField(null=True, blank=True)
    isdir=models.BooleanField(default=False, blank=True)
    schema = models.CharField(max_length=20, default='AES')


    def __str__(self):
        return str(self.path)

    class Meta:
        unique_together = ("owner", "path")


