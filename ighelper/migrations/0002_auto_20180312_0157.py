# Generated by Django 2.0.3 on 2018-03-12 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ighelper', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='image',
            field=models.URLField(max_length=255),
        ),
        migrations.AlterField(
            model_name='media',
            name='location',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='media',
            name='text',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
