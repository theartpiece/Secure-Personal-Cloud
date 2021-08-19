# Generated by Django 2.1.2 on 2018-11-21 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20181103_1943'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='isdir',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='file',
            name='docfile',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='sha256',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
