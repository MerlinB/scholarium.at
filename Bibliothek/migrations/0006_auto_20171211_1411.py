# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-11 14:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Bibliothek', '0005_auto_20171106_1407'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='buch',
            options={'ordering': ['-zeit_erstellt'], 'verbose_name': 'Buch', 'verbose_name_plural': 'Bücher'},
        ),
    ]
