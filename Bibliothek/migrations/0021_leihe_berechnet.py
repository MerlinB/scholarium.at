# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-28 11:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bibliothek', '0020_auto_20180528_1017'),
    ]

    operations = [
        migrations.AddField(
            model_name='leihe',
            name='berechnet',
            field=models.DateField(blank=True, null=True),
        ),
    ]