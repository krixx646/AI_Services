from django.contrib import admin
from .models import PageView, Event, BotVisit


@admin.register(BotVisit)
class BotVisitAdmin(admin.ModelAdmin):
    list_display = ('bot_type', 'path', 'ip_address', 'timestamp')
    list_filter = ('bot_type', 'timestamp')
    search_fields = ('path', 'user_agent', 'ip_address', 'bot_type')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        # Bot visits are auto-created only
        return False


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('path', 'user', 'ip_address', 'browser', 'device', 'timestamp')
    list_filter = ('browser', 'device', 'os', 'timestamp')
    search_fields = ('path', 'url', 'ip_address', 'user__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_name', 'user', 'page_url', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('event_name', 'page_url', 'user__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
