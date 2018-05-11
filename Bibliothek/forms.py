from django import forms
from .models import Zotero_Buch
from Produkte.models import KlasseMitProdukten


class SearchForm(forms.Form):
    search = forms.CharField(required=False, max_length=100, label='Suche')


class FilterForm(forms.Form):
    choices = [(format, KlasseMitProdukten.format_text(format)) for format in Zotero_Buch.arten_liste]

    type = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple,
                                     label='Verfügbarkeit')
