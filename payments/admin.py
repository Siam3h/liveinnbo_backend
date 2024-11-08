from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('email', 'event', 'amount', 'verified')
    search_fields = ('email', 'event__title')
    list_filter = ('verified',)
