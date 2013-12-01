from django.contrib import admin
from gcalsync.models import SyncedCalendar, SyncedEvent

class SyncedCalendarAdmin(admin.ModelAdmin):
    readonly_fields = ('calendar_id',)

admin.site.register(SyncedCalendar, SyncedCalendarAdmin)
admin.site.register(SyncedEvent)