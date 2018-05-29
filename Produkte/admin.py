from django.contrib import admin
from .models import Purchase


class PurchaseAdmin(admin.ModelAdmin):
    list_filter = ['time']


admin.site.register(Purchase, PurchaseAdmin)
