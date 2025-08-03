from django.contrib import admin
from .models import Event, TicketType

class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'category', 'start_time', 'end_time', 'status', 'capacity')
    list_filter = ('status', 'category', 'start_time')
    search_fields = ('title', 'description', 'location', 'organizer__username')
    inlines = [TicketTypeInline]

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'quantity')
    list_filter = ('event',)
    search_fields = ('name', 'event__title')
