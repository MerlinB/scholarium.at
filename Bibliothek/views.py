from django.http import HttpResponseRedirect
import re
import os
from .models import Buch
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from pyzotero import zotero
from .forms import SearchForm


@login_required
def liste_buecher(request):
    zot = zotero.Zotero(settings.ZOTERO_USER_ID, settings.ZOTERO_LIBRARY_TYPE, settings.ZOTERO_API_KEY)
    parameters = {}

    search = request.GET.get('search')
    if search:
        parameters['q'] = search

    parameters['limit'] = 25

    sort = request.GET.get('sort')
    if sort:
        direction = request.GET.get('dir', 'asc')
        parameters['sort'] = sort
        parameters['direction'] = direction
        print(sort, direction)

    page = request.GET.get('seite')

    show = 10
    if page:
        start = show * (int(page) - 1)
        parameters['limit'] = show
        parameters['start'] = start

    buecher = zot.items(**parameters)
    total = int(zot.request.headers['Total-Results'])

    paginator = {
        'page_range': range(int(round(total / show + 0.5))),
        'num_pages': total
    }

    print(request.GET.urlencode())  # TODO: seite ersetzen, statt alles ersetzen.

    context = {
        'buecher': buecher,
        'paginator': paginator,
        'form': SearchForm
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
