# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-04-29 16:30
from __future__ import unicode_literals

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Grundgeruest', '0003_mitwirkende'),
    ]

    operations = [
        migrations.AddField(
            model_name='scholariumprofile',
            name='land1',
            field=django_countries.fields.CountryField(max_length=2, null=True),
        ),
    ]
