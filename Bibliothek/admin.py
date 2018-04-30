from django.contrib import admin

from .models import Buch, Zotero_Buch, Autor, Kollektion


@admin.register(Buch)
class BuchAdmin(admin.ModelAdmin):
    list_display = ('autor', 'titel', 'herausgeber', 'bezeichnung', 'ob_pdf', 'ob_mobi', 'ob_epub')
    list_filter = ['jahr']
    search_fields = ['bezeichnung']


admin.site.register(Zotero_Buch)
admin.site.register(Autor)
admin.site.register(Kollektion)
