from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.conf import settings
from django.contrib import messages
# from easycart.cart import CartException
# from django.views.generic import View
from pyzotero import zotero
from slugify import slugify
from pyzotero.zotero_errors import ResourceNotFound
from easycart import BaseCart
from Grundgeruest.views import Nachricht
from .models import Product
# from Veranstaltungen.models import Veranstaltung, Studiumdings
from Bibliothek.models import Zotero_Buch
# from datetime import date


class Warenkorb(BaseCart):
    def get_queryset(self, pks):
        """ Gibt Liste der Objekte zu den übergebenen pks zurück. """
        return Product.objects.filter(pk__in=pks)

    def process_object(self, obj):
        return Product.objects.get_subclass(id=obj.pk)

    def count_total_price(self):
        """ Berechnet die Summe mit Versandtkosten. """
        summe = sum((item.total for item in self.items.values()))
        summe += 5 if [item.ob_versand for item in self.items.values()] else 0
        return summe


@login_required
def bestellungen(request):
    """ Übersicht der abgeschlossenen Bestellungen"""

    nutzer = request.user.profile
    kaeufe = nutzer.purchases_set.all()

    return render(request, 'Produkte/bestellungen.html', {'kaeufe': kaeufe})


def kaufen(request):
    warenkorb = Warenkorb(request)
    nutzer = request.user.profile
    if nutzer.guthaben < warenkorb.count_total_price():
        messages.error(request, 'Ihr Guthaben reicht leider nicht aus. Laden Sie ihr Guthaben auf, '
                                'indem Sie ihre Unterstützung erneuern.')
        return HttpResponseRedirect(reverse('Produkte:warenkorb'))

    if warenkorb.ob_versand:
        request.user.profile.guthaben += -5
        Nachricht.bestellung_versenden(request)

    warenkorb.empty()

    return HttpResponseRedirect(reverse('Produkte:bestellungen'))


def medien_runterladen(request):
    """ bekommt als POST, welches Objekt heruntergeladen werden soll, prüft
    ob der user das darf, und gibt response mit Anhang zurück """
    import os

    kauf = get_object_or_404(Kauf, id=request.POST['kauf_id'])
    if not kauf.nutzer.user == request.user:
        return 404
    # sonst setze fort, falls der Nutzer das darf:

    obj, art = kauf.objekt_ausgeben(mit_art=True)
    filefield = obj.datei if art == 'aufzeichnung' else getattr(obj, art)

    if isinstance(obj, Zotero_Buch):
        zot = zotero.Zotero(settings.ZOTERO_USER_ID, settings.ZOTERO_LIBRARY_TYPE, settings.ZOTERO_API_KEY)
        print(getattr(obj, art))
        try:
            medium = zot.file(getattr(obj, art))
        except ResourceNotFound:
            raise Http404()
        
        response = HttpResponse(medium, content_type='application/force-download')
        response['Content-Disposition'] = ('attachment; filename=%s.%s' % (slugify(obj.bezeichnung), art))

    else:
        with open(filefield.path, 'rb') as datei:
            medium = datei.read()

        name, ext = os.path.splitext(filefield.name)

        response = HttpResponse(medium, content_type='application/force-download')
        response['Content-Disposition'] = ('attachment; filename=' + obj.slug + ext)

    return response
