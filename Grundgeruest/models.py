from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile, UserenaSignup
from userena.utils import generate_sha1
import random
from django_countries.fields import CountryField
import datetime
from Produkte.models import ProductBase


class Nutzer(AbstractUser):
    @staticmethod
    def erzeuge_zufall(laenge, sonderzeichen=3):
        s = ['abcdefghijkmnopqrstuvwxyz',
             'ABCDEFGHJKLMNPQRSTUVWXYZ',
             '23456789_-',
             '@.%&+!$?/()#*']
        zufall = []
        for i in range(laenge):
            zufall.append(random.sample(s[i % sonderzeichen], 1)[0])
        return ''.join(zufall)

    @staticmethod
    def erzeuge_pw():
        return Nutzer.erzeuge_zufall(7, sonderzeichen=4)

    @staticmethod
    def erzeuge_username():
        return Nutzer.erzeuge_zufall(12)

    @classmethod
    def leeren_anlegen(cls):
        username = cls.erzeuge_username()

        nutzer = UserenaSignup.objects.create_user(username,
                                                   email='spam@spam.de',
                                                   password='spam',
                                                   active=False,
                                                   send_email=False)

        signup = nutzer.userena_signup
        salt, hash = generate_sha1(nutzer.username)
        signup.activation_key = hash
        signup.save()

        return nutzer

    def versende_activation(self):
        """ Autogeneriere pw und versende activation mail incl. pw """
        # activation Mail mit pw versenden
        from userena.mail import UserenaConfirmationMail
        import userena.settings as userena_settings
        from django.contrib.sites.models import Site
        from userena.utils import get_protocol

        signup = self.userena_signup
        password = self.erzeuge_pw()

        context = {'user': signup.user,
                   'without_usernames': userena_settings.USERENA_WITHOUT_USERNAMES,
                   'protocol': get_protocol(),
                   'activation_days': userena_settings.USERENA_ACTIVATION_DAYS,
                   'activation_key': signup.activation_key,
                   'site': Site.objects.get_current(),
                   'passwort': password}

        mailer = UserenaConfirmationMail(context=context)
        mailer.generate_mail("activation")
        mailer.send_mail(signup.user.email)

        self.set_password(password)
        self.save()

    @classmethod
    def neuen_erstellen(cls, email):
        """ Erstellt neuen Nutzer mit angegebener Mailadresse

        Es wird die Methode von UserenaSignup verwendet, sodass gleich-
        zeitig ein signup-Objekt für den Nutzer sowie alle UserObjectPer-
        missions erzeugt werden.
        Ich erstelle auch gleich ein Profil dazu, zur Vollständigkeit.
        Es wird ein Passwort per Zufall gesetzt und an die confirmation
        mail übergeben.
        """
        nutzer = Nutzer.leeren_anlegen()
        nutzer.email = email
        nutzer.save()
        nutzer.versende_activation()
        return nutzer

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.erzeuge_zufall(16)
        super(Nutzer, self).save(*args, **kwargs)

    def __str__(self):
        return '{} {} ({})'.format(self.first_name, self.last_name, self.email)


class ScholariumProfile(UserenaBaseProfile):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='profile')
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
        max_length=10,
        null=True, blank=True)
    ort = models.CharField(
        max_length=30,
        null=True, blank=True)
    land = CountryField(
        blank_label='- Bitte Ihr Land auswählen -',
        null=True)
    guthaben = models.SmallIntegerField(default=0)
    titel = models.CharField(
        max_length=30,
        null=True, blank=True)
    anredename = models.CharField(
        max_length=30,
        null=True, blank=True)

    def get_aktiv(self):
        '''Gibt HÖCHSTE aktive Unterstützung zurück'''
        stufen = self.unterstuetzung_set.all().order_by('-stufe__spendenbeitrag')
        aktiv = [u for u in stufen if u.get_ablauf() >= date.today()]
        return aktiv[0] if aktiv else None

    def get_stufe(self):
        '''Gibt HÖCHSTE aktive Stufe zurück.'''
        aktiv = self.get_aktiv()
        return aktiv.stufe if aktiv else None

    def get_ablauf(self):
        '''Gibt das Ablaufdatum der NEUSTEN Unterstützung zurück.'''
        u = self.unterstuetzung_set.all().order_by('-datum')
        return u[0].get_ablauf() if u else None

    def get_Status(self):
        status = [
            (0, "Kein Unterstützer"),
            (1, "Abgelaufen"),
            (2, "30 Tage bis Ablauf"),
            (3, "Aktiv")
        ]
        if self.get_ablauf():
            verbleibend = (self.get_ablauf() - datetime.now().date()).days
            if verbleibend < 0:
                return status[1]
            elif verbleibend < 30:
                return status[2]
            else:
                return status[3]
        else:
            return status[0]

    def guthaben_aufladen(self, betrag):
        """ wird spaeter nuetzlich, wenn hier mehr als die eine Zeile^^ """
        self.guthaben += int(betrag)
        self.save()

    def adresse_ausgeben(self):
        return """%s
%s
%s %s
%s""" % (self.user.get_full_name(), self.strasse, self.plz, self.ort, self.land.name if self.land else '')

    def get_leihe_aktiv(self):
        return [leihe for leihe in self.leihe_set.all() if leihe.get_ablauf >= date.today()]

    def __str__(self):
        return '%s (%s)' % (self.user.get_full_name(), self.user.email)

    class Meta():
        verbose_name = 'Nutzerprofil'
        verbose_name_plural = 'Nutzerprofile'


class DonationLevel(ProductBase):
    id = models.IntegerField(primary_key=True)
    amount = models.SmallIntegerField()

    class Meta:
        verbose_name = "Spendenstufe"
        verbose_name_plural = "Spendenstufen"

    def __str__(self):
        return '%s: %s (%d)' % (self.id, self.name, self.amount)
    

class Donation(models.Model):
    DEFAULT_DURATION = datetime.timedelta(days=365)

    profile = models.ForeignKey(ScholariumProfile, on_delete=models.CASCADE)
    level = models.ForeignKey(DonationLevel, on_delete=models.PROTECT)
    date = models.DateField(default=datetime.date.today)
    payment_method = models.CharField(blank=True, max_length=100)
    review = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Unterstützung'
        verbose_name_plural = 'Unterstuetzungen'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.profile.guthaben_aufladen(self.level.amount)
            self.profile.save()
        super(Donation, self).save(*args, **kwargs)

    def __str__(self):
        return '%s: %s (%s)' % (self.profile.user.get_full_name(), self.level.name, self.date)

    def get_expiration(self):
        '''Gibt Ablaufdatum der Unterstützung zurück.'''
        return self.datum + self.DEFAULT_DURATION


class Menue(Grundklasse):
    stufe = models.ManyToManyField(Spendenstufe)


class Menuepunkt(Grundklasse):
    menue = models.ForeignKey(Menue, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['nummer']


class Mitwirkende(models.Model):

    level_choices = [(1, 'Rektor'),
                     (2, 'Gründer'),
                     (3, 'Mitarbeiter'),
                     (4, 'Mentor'),
                     (8, 'Student')]

    name = models.CharField(max_length=100)
    alt_id = models.PositiveSmallIntegerField(default=0)
    text_de = models.TextField(null=True, blank=True)
    text_en = models.TextField(null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    level = models.PositiveSmallIntegerField(default=1,
                                             choices=level_choices)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Mitwirkender"
        verbose_name_plural = "Mitwirkende"
        ordering = ('level', 'start', 'alt_id')

    def __str__(self):
        return self.name
