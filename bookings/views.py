from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Booking
from .serializers import BookingCreateSerializer, BookingListSerializer
from payments.utils import create_stripe_checkout_session  
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import BookingReceiptSerializer







# ------------------------ CREATE Booking View ------------------------
class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        checkout_url = create_stripe_checkout_session(booking)

        return Response({
            "message": "Booking successful. Proceed to payment.",
            "checkout_url": checkout_url
        }, status=status.HTTP_201_CREATED)



# ------------------------ LIST User Bookings ------------------------
class BookingListView(generics.ListAPIView):
    serializer_class = BookingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-booked_at')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": "success",
                "message": "Bookings fetched successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "Failed to fetch bookings.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# ------------------------ Get Order/My Receipts ------------------------

class MyReceiptsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            bookings = Booking.objects.filter(user=user, status='paid').order_by('-booked_at')
            serializer = BookingReceiptSerializer(bookings, many=True)

            return Response({
                "status": "success",
                "message": "Receipts fetched successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "Failed to fetch receipts.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# ------------------------ Get Revenue/Platform fee etc ------------------------

class OrganizerRevenueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Allow only organizers
        if user.role != 'organizer':
            return Response({
                "status": "error",
                "message": "Permission denied. Only organizers can access revenue data."
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            organizer_bookings = Booking.objects.filter(event__organizer=user, status='paid')

            total_revenue = sum(booking.organizer_revenue for booking in organizer_bookings)
            total_platform_fee = sum(booking.platform_fee for booking in organizer_bookings)
            total_bookings = organizer_bookings.count()

            return Response({
                "status": "success",
                "message": "Organizer revenue fetched successfully.",
                "data": {
                    'total_bookings': total_bookings,
                    'total_revenue': float(total_revenue),
                    'total_platform_fee': float(total_platform_fee),
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "Failed to fetch revenue.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
