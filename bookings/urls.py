from django.urls import path
from .views import BookingCreateView, BookingListView, MyReceiptsView, OrganizerRevenueView

urlpatterns = [
    path('create/', BookingCreateView.as_view(), name='booking-create'),
    path('my-bookings/', BookingListView.as_view(), name='booking-list'),
    path('orders/my_receipts/', MyReceiptsView.as_view(), name='my_receipts'),
    path('organizers/revenue/', OrganizerRevenueView.as_view(), name='organizer-revenue'),


]
