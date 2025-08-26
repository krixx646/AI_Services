from django.contrib import admin
from .models import NoteAsset


@admin.register(NoteAsset)
class NoteAssetAdmin(admin.ModelAdmin):
    list_display = ("bot", "uploaded_by", "original_filename", "created_at")
    search_fields = ("original_filename", "bot__reference", "uploaded_by__username", "uploaded_by__email")
    list_filter = ("created_at",)
