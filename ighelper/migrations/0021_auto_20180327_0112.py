# Generated by Django 2.0.3 on 2018-03-27 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ighelper', '0020_instagramusercounter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instagramuser',
            name='instagram_id',
            field=models.BigIntegerField(db_index=True, unique=True),
        ),
        migrations.AlterField(
            model_name='media',
            name='instagram_id',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
