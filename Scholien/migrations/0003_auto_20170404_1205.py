# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-04-04 12:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scholien', '0002_auto_20170404_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buechlein',
            name='bild',
            field=models.ImageField(null=True, upload_to='scholienbuechlein'),
        ),
    ]