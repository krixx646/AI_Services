from django.contrib import admin
from .models import PaymentTransaction, BotInstance


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("reference", "student", "amount", "currency", "status", "created_at")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("reference", "student__username", "student__email")
    ordering = ("-created_at",)


@admin.register(BotInstance)
class BotInstanceAdmin(admin.ModelAdmin):
    list_display = ("reference", "owner", "status", "note_count", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("reference", "owner__username", "owner__email")
    ordering = ("-created_at",)
