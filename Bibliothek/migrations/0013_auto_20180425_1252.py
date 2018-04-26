# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-25 12:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bibliothek', '0012_auto_20180423_1622'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zotero_buch',
            name='ob_epub',
        ),
        migrations.RemoveField(
            model_name='zotero_buch',
            name='ob_mobi',
        ),
        migrations.RemoveField(
            model_name='zotero_buch',
            name='preis_epub',
        ),
        migrations.RemoveField(
            model_name='zotero_buch',
            name='preis_mobi',
        ),
        migrations.AddField(
            model_name='zotero_buch',
            name='pdf',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
