"""
Die Modelle für Projektweite Daten: Menüpunkte, Nutzer/Profile

 - eingegeben wird eine slug (absolut, bezüglich /) und eine nummer, die die
   Reihenfolge im Menü bestimmt
 - was wird an das Template übergeben? Vielleicht lieber eine Liste für jede 
   Nutzerkategorie erstellen? Dann fällt nummer weg. 
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile
from django.core.validators import RegexValidator
import random, string

#from Produkte.models import Produkt
from seite.models import Grundklasse

class Menuepunkt(Grundklasse):
    sichtbar_ab = models.IntegerField(
        blank=True, 
        default=0)
    nummer = models.IntegerField(default=1)

    class Meta:
        abstract = True
        ordering = ['nummer']
            
class GanzesMenue(Grundklasse):
    pass
    
class Hauptpunkt(Menuepunkt):
    gehoert_zu = models.ForeignKey(GanzesMenue)
    class Meta: verbose_name_plural = 'Menü - Hauptpunkte'
    
class Unterpunkt(Menuepunkt):
    gehoert_zu = models.ForeignKey(Hauptpunkt)
    class Meta: verbose_name_plural = 'Menü - Unterpunkte'
    def __str__(self):
        return "{}: {} - {}".format(
            self.gehoert_zu.gehoert_zu.bezeichnung,
            self.gehoert_zu.bezeichnung,
            self.bezeichnung)

class Nutzer(AbstractUser):
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = ''.join(random.sample(string.ascii_lowercase, 20))
        super(Nutzer, self).save(*args, **kwargs)

class ScholariumProfile(UserenaBaseProfile):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='my_profile')
    stufe_choices = [(0, 'Interessent'),
        (1, 'Gast'),
        (2, 'Teilnehmer'),
        (3, 'Scholar'),
        (4, 'Partner'),
        (5, 'Beirat'),
        (6, 'Patron')]
    stufe = models.IntegerField(
        choices=stufe_choices,
        default=0)
    anrede = models.CharField(
        max_length=4,
        choices=[('Herr', 'Herr'), ('Frau', 'Frau')],
        default='Herr', null=True)
    tel = models.CharField(
        max_length=20,
        null=True, blank=True)
    firma = models.CharField(
        max_length=30,
        null=True, blank=True)
    strasse = models.CharField(
        max_length=30,
        null=True, blank=True)
    plz = models.CharField(
        max_length = 5,
        validators=[RegexValidator('^[0-9]+$')],
        null=True, blank=True)
    ort = models.CharField(
        max_length=30,
        null=True, blank=True)
    land = models.CharField(
        max_length=30,
        null=True, blank=True)    
    guthaben = models.SmallIntegerField(default=0)
    titel = models.CharField(
        max_length=30,
        null=True, blank=True)
    anredename = models.CharField(
        max_length=30,
        null=True, blank=True)    
    letzte_zahlung = models.DateField(null=True, blank=True)
    datum_ablauf = models.DateField(null=True, blank=True)
    alt_id = models.SmallIntegerField(
        default=0, editable=False)
    alt_notiz = models.CharField(
        max_length=255, null=True,
        default='', editable=False)    
    alt_scholien = models.SmallIntegerField(
        default=0, null=True, editable=False)
    alt_mahnstufe = models.SmallIntegerField(
        default=0, null=True, editable=False)
    alt_auslaufend = models.SmallIntegerField(
        default=0, null=True, editable=False)
    alt_gave_credits = models.SmallIntegerField(
        default=0, null=True, editable=False)
    alt_registration_ip = models.GenericIPAddressField(
        editable=False, null=True)

    def darf_scholien_sehen(self):
        if self.guthaben < 20:
            return True
        else:
            raise TypeError('Guthaben zu hoch, editiere ScholariumProfile.darf_scholien_sehen()')
        
    class Meta():
        verbose_name = 'Nutzerprofil'
        verbose_name_plural = 'Nutzerprofile'
    

