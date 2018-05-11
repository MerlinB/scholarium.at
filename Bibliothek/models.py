from django.db import models
from Produkte.models import KlasseMitProdukten
from django.urls import reverse
from seite.models import Grundklasse
from django.urls.exceptions import NoReverseMatch


class Kollektion(Grundklasse):
    parent = models.ForeignKey('self', blank=True, null=True)


class Autor(models.Model):
    vorname = models.CharField(max_length=255, blank=True, null=True)
    nachname = models.CharField(max_length=255)

    def __str__(self):
        return '%s %s' % (self.vorname, self.nachname)


class Zotero_Buch(KlasseMitProdukten):
    # TODO: Use django translation instead?
    trans = {
        'Deutsch': ['German', 'de', 'ger'],
        'Englisch': ['English', 'en']
    }
    langs = dict([(v, k) for k, values in trans.items() for v in values])
    arten_liste = ['kaufen', 'leihen', 'druck', 'pdf', 'mobi', 'epub']

    autoren = models.ManyToManyField(Autor)
    jahr = models.DateField(blank=True, null=True)
    sprache = models.CharField(max_length=100, blank=True, null=True)
    pdf = models.CharField(max_length=50, blank=True, null=True)
    mobi = models.CharField(max_length=50, blank=True, null=True)
    epub = models.CharField(max_length=50, blank=True, null=True)
    kollektion = models.ManyToManyField(Kollektion)

    def save(self, *args, **kwargs):
        if self.sprache in self.langs:
            self.sprache = self.langs[self.sprache]
        super().save(*args, **kwargs)


class Altes_Buch(KlasseMitProdukten):
    arten_liste = ['kaufen']
    autor_und_titel = models.CharField(
        max_length=255,
        null=True, blank=True)

    def button_text(self, _):
        return 'Auswählen'


class Buch(KlasseMitProdukten):
    arten_liste = ['kaufen', 'leihen', 'druck', 'pdf', 'mobi', 'epub']
    # druck bedeutet neu und kaufen ist ein gebrauchtes Bibliotheksbuch
    titel = models.CharField(
        max_length=255,
        null=True, blank=True)
    autor = models.CharField(
        max_length=255,
        null=True, blank=True)
    isbn = models.CharField(
        max_length=40,
        null=True, blank=True)
    adresse = models.CharField(
        max_length=100,
        null=True, blank=True)
    ausgabe = models.CharField(
        max_length=100,
        null=True, blank=True)
    herausgeber = models.CharField(
        max_length=100,
        null=True, blank=True)
    serie = models.CharField(
        max_length=100,
        null=True, blank=True)
    notiz = models.CharField(
        max_length=100,
        null=True, blank=True)
    jahr = models.CharField(
        max_length=4,
        null=True, blank=True)
    sprache = models.CharField(
        max_length=3,
        null=True, blank=True)
    exlibris = models.CharField(
        max_length=40,
        null=True, blank=True)
    stichworte = models.CharField(
        max_length=255,
        null=True, blank=True)
    zusammenfassung = models.TextField(
        null=True, blank=True)
    pdf = models.FileField(upload_to='buecher', null=True, blank=True)
    epub = models.FileField(upload_to='buecher', null=True, blank=True)
    mobi = models.FileField(upload_to='buecher', null=True, blank=True)
    bild = models.ImageField(upload_to='buecher', null=True, blank=True)
    alte_nr = models.SmallIntegerField(null=True, editable=False)

    def get_absolute_url(self):
        try:
            return reverse('Bibliothek:detail_buch_alt', kwargs={'slug': self.slug})
        except NoReverseMatch:
            return '#'

    def preis_ausgeben(self, art):
        if art == 'leihen':
            return self.finde_preis(art) or 13
        elif art == 'kaufen':
            return self.finde_preis(art) or 37
        elif art in ['pdf', 'epub', 'mobi']:
            return self.finde_preis(art) or 5
        elif art == 'druck':
            return self.finde_preis(art) or 20

    def button_text(self, art):
        return art.capitalize()

    def save(self, *args, **kwargs):
        if not self.bezeichnung:
            self.bezeichnung = "%s: %s" % (self.autor, self.titel)
        return super().save(*args, **kwargs)

    def anzeigemodus(self, art):
        from Produkte.models import arten_attribute
        if arten_attribute[art][0] and self.finde_anzahl(art) > 1:
            return 'mit_menge'
        elif arten_attribute[art][0] and self.finde_anzahl(art) == 0:
            return 'verbergen'
        elif arten_attribute[art][0]:  # beschränkt, genau eins
            return 'ohne_menge'
        elif getattr(self, 'ob_'+art) and bool(getattr(self, art)):
            # wenn unbeschränkt, gucke nach Datei und ob aktiviert
            return 'inline'
        else:
            return 'verbergen'

    class Meta:
        verbose_name_plural = 'Bücher'
        verbose_name = 'Buch'
        ordering = ['-zeit_erstellt']
