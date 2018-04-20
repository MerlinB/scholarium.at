from django.http import HttpResponseRedirect, HttpResponse
import re
import os
from .models import Buch
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from pyzotero import zotero
from pprint import pprint


@login_required
def liste_buecher(request):
    zot = zotero.Zotero(settings.ZOTERO_USER_ID, settings.ZOTERO_LIBRARY_TYPE, settings.ZOTERO_API_KEY)
    buecher = zot.top(limit=5)
    pprint(buecher)

    page = request.GET.get('seite')
    sort = request.GET.get('sort', '')

    if sort:
        sort = "-" + sort if request.GET.get('dir', '') == 'desc' else sort
        buecher = buecher.order_by(sort)

    paginator = Paginator(buecher, 20)
    try:
        buecher = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        buecher = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        buecher = paginator.page(paginator.num_pages)

    context = {
        'buecher': buecher,
        'paginator': paginator
    }
    return render(request, 'Bibliothek/buecher.html', context)


@login_required
def detail_buch(request, id):
    zot = zotero.Zotero(settings.ZOTERO_USER_ID, settings.ZOTERO_LIBRARY_TYPE, settings.ZOTERO_API_KEY)
    buch = zot.item(id)
    return render(request, 'Bibliothek/detail_buch.html', {'buch': buch})


attributnamen = {
    'author': 'autor',
    'isbn': 'isbn',
    'title': 'titel',
    'address': 'adresse',
    'edition': 'ausgabe',
    'publisher': 'herausgeber',
    'keywords': 'stichworte',
    'language': 'sprache',
    'note': 'notiz',
    'abstract': 'zusammenfassung',
    'series': 'serie',
    'year': 'jahr'}


@transaction.atomic
def aus_datei_einlesen(request, exlibris=''):
    f = open(os.path.join(settings.MEDIA_ROOT, 'buchliste'), 'r')
    text = f.read()[7:-2]  # an die bibtex-Ausgabe von zotero angepasst
    f.close()

    trennung = re.compile('\}\n\n(?P<name>[@, \w]*)\{')
    liste = trennung.sub('XXX', text).split('XXX')
    for buch in liste:
        zeilen = buch.split(',\n\t')
        teilsplit = re.compile(r'(\w+) = \{(.*)\}')
        bezeichnung = zeilen[0]
        matches = [teilsplit.match(zeile) for zeile in zeilen[1:]]
        daten = dict([match.groups() for match in matches if match])

        buch = Buch.objects.create(bezeichnung=bezeichnung)
        buch.exlibris = exlibris
        for key in daten:
            if key in attributnamen:
                setattr(buch, attributnamen[key], daten[key])
        buch.save()

    return HttpResponseRedirect('/warenkorb/')
