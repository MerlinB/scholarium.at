from django import forms


class SearchForm(forms.Form):

    choices = [
        ('pdf', 'PDF'),
        ('epub', 'EPUB'),
        ('druck', 'Druckausgabe'),
        ('leih', 'Leihgabe'),
    ]

    search = forms.CharField(required=False, max_length=100, label='Suche')
    # Geht nicht bei direkter API-Implementierung:
    # type = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple,
    #                                  label='Verfügbarkeit')
