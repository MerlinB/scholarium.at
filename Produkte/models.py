from django.db import models
from Grundgeruest.models import ScholariumProfile
from model_utils.managers import InheritanceManager
from autoslug import AutoSlugField


class ProductBase(models.Model):
    """Parent Class for all Product Type Classes."""

    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', unique=True)
    description = models.TextField(null=True, blank=True)
    objects = InheritanceManager()


class Product(models.Model):
    """Purchaseable products."""

    type = models.ForeignKey(ProductBase, on_delete=models.CASCADE)
    price = models.IntegerField()
    limited = models.BooleanField(default=True)
    amount = models.IntegerField(null=True, bank=True)
    shipping = models.BooleanField(default=False)
    file = models.FileField(null=True, blank=True)

    class Meta():
        verbose_name = 'Produkt'
        verbose_name_plural = 'Produkte'


class Purchase(models.Model):
    """Logs purchases."""

    profile = models.ForeignKey(ScholariumProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.SmallIntegerField(blank=True, default=1)
    time = models.DateTimeField(auto_now_add=True, editable=False)
    comment = models.CharField(max_length=255, blank=True)
    balance_before = models.SmallIntegerField(editable=False)
    shipped = models.DateField(blank=True, null=True)

    def __str__(self):
        return '%dx %s (%s)' % (self.amount, self.product.__str__(), self.user.__str__())

    class Meta():
        verbose_name = 'Kauf'
        verbose_name_plural = 'Käufe'
