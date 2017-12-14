from django.http import HttpResponseRedirect
import re
import os
from . import models
from django.db import transaction
from django.conf import settings
from Grundgeruest.views import ListeMitMenue


class ListeBuecher(ListeMitMenue):
    template_name = 'Bibliothek/buecher_alt.html'
    model = models.Buch
    context_object_name = 'buecher'
    paginate_by = 80

    def get_queryset(self):
        sort = self.request.GET.get('sort', '')
        if sort:
            sort = "-" + sort if self.request.GET.get('dir', '') == 'desc' else sort
            return models.Buch.objects.all().order_by(sort)
        else:
            return models.Buch.objects.all()


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

        buch = models.Buch.objects.create(bezeichnung=bezeichnung)
        buch.exlibris = exlibris
        for key in daten:
            if key in attributnamen:
                setattr(buch, attributnamen[key], daten[key])
        buch.save()

    return HttpResponseRedirect('/warenkorb/')
