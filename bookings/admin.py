from django.contrib import admin
from .models import Booking, BookedTicket

class BookedTicketInline(admin.TabularInline):
    model = BookedTicket
    extra = 1  # how many empty forms to show

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'total_amount', 'booked_at')
    list_filter = ('event', 'booked_at')
    search_fields = ('user__username', 'event__title')
    inlines = [BookedTicketInline]

@admin.register(BookedTicket)
class BookedTicketAdmin(admin.ModelAdmin):
    list_display = ('booking', 'ticket_type', 'quantity')
    list_filter = ('ticket_type',)
