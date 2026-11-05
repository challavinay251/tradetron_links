
from django.contrib import admin
from .models import TradeTronSettings


@admin.register(TradeTronSettings)
class TradeTronSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'is_enabled', 'updated_at')
    list_editable = ('is_enabled',)
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Allow only one settings record.
        return not TradeTronSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
