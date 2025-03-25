from django.contrib import admin
from .models import Player, Transaction, Game

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'balance', 'credits', 'debits', 'purchases', 'attendance', 'frequency', 'value_per_day')
    search_fields = ('name', 'username')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('player', 'amount', 'transaction_type', 'description', 'date')
    search_fields = ('player__name', 'transaction_type')
    list_filter = ('transaction_type', 'date')

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('start_time',)