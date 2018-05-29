from django.db import models
from Produkte.models import ProductBase, Product
from django.core.urlresolvers import reverse


class EventType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1200, null=True, blank=True)
    time_start = models.TimeField()
    time_end = models.TimeField()

    class Meta:
        verbose_name = 'Veranstaltungsart'
        verbose_name_plural = "Veranstaltungsarten"


class Event(ProductBase):
    date = models.DateField()
    type = models.ForeignKey(EventType)

    class Meta:
        verbose_name_plural = "Veranstaltungen"
        verbose_name = "Veranstaltung"

    def __str__(self):
        return '%s: %s' % (self.type.name, self.name)


class Livestream(Product):
    link = models.CharField(max_length=100)
    chat = models.BooleanField(default=False)

    def embed_link(self):
        return self.link.replace('watch?v=', 'embed/')


class StudyProgram(ProductBase):

    class Meta:
        verbose_name = "Studienprogramm"
        verbose_name_plural = "Studienprogramme"

    def get_absolute_url(self):
        return reverse('studium_detail', kwargs={'slug': self.slug})
