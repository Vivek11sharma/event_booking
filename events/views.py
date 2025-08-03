from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework import generics
from django.db.models import Q

from .models import Event
from .serializers import EventSerializer
from rest_framework.permissions import AllowAny


# --------- Organizer Access Permission ---------
class IsOrganizer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'organizer'

    def has_object_permission(self, request, view, obj):
        return obj.organizer == request.user


# --------- Organizer's CRUD ViewSet ---------
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        return self.queryset.filter(organizer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            event = serializer.save(organizer=request.user)
            response_data = EventSerializer(event).data

            return Response({
                "status": "success",
                "message": "Event created successfully.",
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "error",
            "message": "Failed to create event.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "status": "success",
            "message": "Events fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            event = serializer.save()
            return Response({
                "status": "success",
                "message": "Event updated successfully.",
                "data": self.get_serializer(event).data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "Failed to update event.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "status": "success",
                "message": "Event deleted successfully."
            },
            status=status.HTTP_200_OK
        )



# --------- Public Event Discovery View ---------
class PublicEventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        allowed_params = {'location', 'category', 'title', 'date'}
        request_params = set(self.request.query_params.keys())


        if not request_params.issubset(allowed_params):
            return Event.objects.none()

        queryset = Event.objects.filter(status='published')

        # Case-insensitive filters
        location = self.request.query_params.get('location')
        category = self.request.query_params.get('category')
        title = self.request.query_params.get('title')
        date = self.request.query_params.get('date')  # Format: YYYY-MM-DD

        if location:
            queryset = queryset.filter(location__icontains=location)
        if category:
            queryset = queryset.filter(category__icontains=category)
        if title:
            queryset = queryset.filter(title__icontains=title)
        if date:
            queryset = queryset.filter(start_time__date=date)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                "status": "success",
                "message": "No matching events found.",
                "data": []
            }, status=status.HTTP_200_OK)


        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "status": "success",
                "message": "Events fetched successfully.",
                "data": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "Events fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
