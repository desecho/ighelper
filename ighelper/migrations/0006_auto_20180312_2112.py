# Generated by Django 2.0.3 on 2018-03-13 01:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ighelper', '0005_follower_followed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='follower',
            name='friend',
        ),
        migrations.RemoveField(
            model_name='user',
            name='instagram_id',
        ),
    ]
