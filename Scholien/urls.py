from django.conf.urls import url

from . import views
from .views import liste_artikel, liste_buechlein, ein_artikel, ein_buechlein

app_name = 'Scholien'

urlpatterns = [
    url(r'^/$', liste_artikel, name='index'),
    url(r'^buechlein/$', liste_buechlein, name='buechlein_liste'),
    url(r'^/(?P<slug>[-\w]+)/$', ein_artikel, name='artikel_detail'),
    url(r'^buechlein/(?P<slug>[-\w]+)/$', ein_buechlein, name='buechlein_detail'),
    url(r'^aus_datei_einlesen$',
        views.daten_einlesen,
        name='aus_datei_einlesen'),
    ]
