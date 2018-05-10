from django.conf.urls import url

from .views import aus_datei_einlesen
from Bibliothek.views import liste_buecher, detail_buch, collection

app_name = 'Bibliothek'

urlpatterns = [
    url(r'^$', liste_buecher, name='liste_buecher'),
    url(r'^(?P<collection>[\w]*)$', collection, name='collection'),
    url(r'^buch/(?P<id>[\w-]+)$', detail_buch, name='detail_buch'),
    url('^aus_datei_einlesen/([\w-]*)$', aus_datei_einlesen, name='einlesen'),
    url('^aus_datei_einlesen$', aus_datei_einlesen, name='einlesen'),
]
