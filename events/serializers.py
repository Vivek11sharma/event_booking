from rest_framework import serializers
from .models import Event, TicketType

class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ['id', 'name', 'price', 'quantity']

class EventSerializer(serializers.ModelSerializer):
    ticket_types = TicketTypeSerializer(many=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'location', 'category', 'start_time', 'end_time', 'status', 'capacity', 'ticket_types' ]

    def create(self, validated_data):
        ticket_data = validated_data.pop('ticket_types')
        event = Event.objects.create(**validated_data)
        for ticket in ticket_data:
            TicketType.objects.create(event=event, **ticket)
        return event

    def update(self, instance, validated_data):
        ticket_data = validated_data.pop('ticket_types', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update ticket types (you can enhance this)
        instance.ticket_types.all().delete()
        for ticket in ticket_data:
            TicketType.objects.create(event=instance, **ticket)

        return instance
