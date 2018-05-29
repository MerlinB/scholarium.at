from django.db import models
from Produkte.models import ProductBase, Purchase
from django.urls import reverse
from seite.models import BaseClass
from django.urls.exceptions import NoReverseMatch


class Collection(BaseClass):
    parent = models.ForeignKey('self', blank=True, null=True)


class Author(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Book(ProductBase):
    authors = models.ManyToManyField(Author)
    year = models.DateField(blank=True, null=True)
    collection = models.ManyToManyField(Collection)

    def get_absolute_url(self):
        try:
            return reverse('Bibliothek:detail_buch', kwargs={'id': self.slug})
        except NoReverseMatch:
            return '#'

    def get_lendings(self):
        return self.lending_set.filter(returned__isnull=True)

    def get_lendings_possible(self):
        return self.product_set.get(name='Leihe').amount - len(self.get_lendings())

    def __str__(self):
        return 'Buch: %s (%s)' % (self.name, ', '.join(self.authors.all()))

    class Meta:
        verbose_name = 'Buch'
        verbose_name_plural = 'Bücher'


class Lending(Purchase):
    returned = models.DateField(blank=True, null=True)
    charged = models.DateField(blank=True, null=True)

    def __str__(self):
        return 'Leihe %s: %s' % (self.profile.__str__(), self.product.__str__())

    class Meta:
        verbose_name = 'Leihe'
        verbose_name_plural = 'Leihen'
