# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-05-05 12:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Grundgeruest', '0009_auto_20170505_1406'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mitwirkende',
            name='id_old',
        ),
    ]
