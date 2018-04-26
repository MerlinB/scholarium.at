from django.http import HttpResponseRedirect
import re
import os
from .models import Buch, Zotero_Buch, Autor
from django.db import transaction
from django.db.models import Q, Value
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from pyzotero import zotero
from .forms import SearchForm
from pprint import pprint
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import Concat


@login_required
def liste_buecher(request):
    '''Gibt die Bibliotheks-Tabelle aus.
    '''

    sort = request.GET.get('sort')
    search = request.GET.get('search')
    page = request.GET.get('seite')
    types = request.GET.getlist('type')

    # Filter for search term
    if search:
        buecher = Zotero_Buch.objects.annotate(autoren__name=Concat('autoren__vorname', Value(' '), 'autoren__nachname')) \
                                     .filter(Q(bezeichnung__icontains=search) | Q(autoren__name__icontains=search))
        buecher = buecher.distinct()
    else:
        buecher = Zotero_Buch.objects.all()

    # Filter for format type
    if types:
        types_dict = {}
        for type in types:
            types_dict['ob_%s' % type] = True
            types_dict['%s__isnull' % type] = False
        buecher = buecher.filter(**types_dict)

    # Table sort
    if sort:
        sort = "-" + sort if request.GET.get('dir', '') == 'desc' else sort
        buecher = buecher.order_by(sort)
    else:
        buecher = buecher.order_by('-jahr')

    # Pagination
    paginator = Paginator(buecher, 10)
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
