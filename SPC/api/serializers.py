import hashlib

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ModelField
from user.models import File


class DataField(serializers.Field):
    def to_representation(self, value):
        return value.docfile

    def get_value(self, instance):
        if 'isdir' not in instance.keys():
            return [0, instance['docfile']]
        elif instance['isdir']=='True':
            return [1, None]
        elif 'docfile' in instance.keys():
            return [0, instance['docfile']]
        else:
            return [0,None]

    def to_internal_value(self, data):
        if data[0]==0:

            ret = {
                'docfile': data[1].encode('utf-8'),
            }
        else:
            ret = {
                'docfile': None,
            }
        return ret



class ShaField(serializers.Field):

    def to_representation(self, value):
        return value.sha256

    def get_value(self, instance):
        sha256=None
        if 'sha256' in instance.keys():
            sha256=instance['sha256']
        if 'isdir' not in instance.keys():
            return [0, instance['docfile'], sha256]
        elif instance['isdir']=='True':
            return [1, None, sha256]
        elif 'docfile' in instance.keys():
            # print(instance['sha256'])
            return [0, instance['docfile'], sha256]
        else:
            return [0, None, sha256]

    def to_internal_value(self, data):
        # print(type(data[0]))
        # print(data[0])
        if data[0]==0:
            # if data[1]==None:
            #     raise
            sha = hashlib.sha256()
            sha.update(data[1].encode('utf-8'))
            sha256 = sha.hexdigest()
            if sha256!=data[2]:
                raise ValueError({'message': 'hash mismatch'})
            ret = {
                'sha256': sha256,
            }
        else:
            ret = {
                'sha256': None,
            }
        return ret

class FileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    docfile = DataField(source='*')
    try:
        sha256 = ShaField(source='*')
    except:
        raise ValidationError({'message': 'hash mismatch'})
    class Meta:
        model = File
        fields = ('owner', 'path', 'sha256', 'docfile', 'isdir', 'schema')


class FileListSerializer(serializers.ModelSerializer):
    # owner = serializers.ReadOnlyField(source='owner.username')
    sha256 = ShaField(source='*')
    class Meta:
        model = File
        fields = ('path', 'sha256', 'isdir', 'schema')
