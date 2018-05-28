from django.contrib import admin

from .models import Buch, Zotero_Buch, Autor, Kollektion, Leihe


@admin.register(Buch)
class BuchAdmin(admin.ModelAdmin):
    list_display = ('autor', 'titel', 'herausgeber', 'bezeichnung', 'ob_pdf', 'ob_mobi', 'ob_epub')
    list_filter = ['jahr']
    search_fields = ['bezeichnung']


@admin.register(Zotero_Buch)
class ZoteroBuchAdmin(admin.ModelAdmin):
    raw_id_fields = ['autoren']
    search_fields = ['bezeichnung']
    list_display = ['bezeichnung', 'get_authors']
    list_filter = ['jahr']

    def get_authors(self, obj):
        return ", ".join([autor.__str__() for autor in obj.autoren.all()])


@admin.register(Leihe)
class LeihAdmin(admin.ModelAdmin):
    raw_id_fields = ['buch', 'nutzer', 'kauf']
    list_display = ['nutzer', 'buch', 'versandt', 'rueckkehr']


admin.site.register(Autor)
admin.site.register(Kollektion)
