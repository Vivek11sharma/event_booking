from rest_framework import serializers
from .models import Booking, BookedTicket
from events.models import TicketType, Event
from events.serializers import TicketTypeSerializer


# ---------------------- Input Ticket (for creating) ----------------------
class BookedTicketInputSerializer(serializers.Serializer):
    ticket_type_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)

# ---------------------- Output Ticket (for showing data) ----------------------
class BookedTicketOutputSerializer(serializers.ModelSerializer):
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    price_per_ticket = serializers.DecimalField(source='ticket_type.price', max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = BookedTicket
        fields = ['ticket_type_name', 'quantity', 'price_per_ticket', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.ticket_type.price * obj.quantity



# ---------------------- Booking CREATE Serializer ----------------------
class BookingCreateSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(write_only=True)
    tickets = BookedTicketInputSerializer(many=True, write_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'event_id', 'tickets']

    def validate(self, data):
        event_id = data.get('event_id')
        tickets = data.get('tickets', [])


        if not tickets:
            raise serializers.ValidationError("At least one ticket must be selected.")


        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Invalid event ID.")


        for ticket in tickets:
            ticket_type_id = ticket.get('ticket_type_id')
            quantity = ticket.get('quantity')

            if ticket_type_id is None:
                raise serializers.ValidationError("Each ticket must include 'ticket_type_id'.")

            try:
                ticket_type = TicketType.objects.get(id=ticket_type_id)
            except TicketType.DoesNotExist:
                raise serializers.ValidationError(f"Ticket type {ticket_type_id} not found.")

            if ticket_type.event_id != event_id:
                raise serializers.ValidationError(f"Ticket type {ticket_type.id} does not belong to the given event.")

            if quantity > ticket_type.quantity:
                raise serializers.ValidationError(f"Not enough tickets available for {ticket_type.name}.")

        return data

    def create(self, validated_data):
        tickets_data = validated_data.get('tickets')
        event_id = validated_data.get('event_id')
        event = Event.objects.get(id=event_id)
        user = self.context['request'].user

        total_amount = 0
        booking = Booking.objects.create(user=user, event=event, total_amount=0)

        for ticket in tickets_data:
            ticket_type = TicketType.objects.get(id=ticket['ticket_type_id'])
            quantity = ticket['quantity']

            BookedTicket.objects.create(
                booking=booking,
                ticket_type=ticket_type,
                quantity=quantity
            )

            total_amount += ticket_type.price * quantity

        booking.total_amount = total_amount
        booking.save()
        return booking


# ---------------------- Booking LIST Serializer ----------------------
class BookingListSerializer(serializers.ModelSerializer):
    booked_tickets = BookedTicketOutputSerializer(source='tickets', many=True, read_only=True)  # Changed from 'bookedticket_set' to 'tickets'
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'event', 'event_title', 'total_amount', 'booked_at', 'booked_tickets']


# ---------------------- Booking Receipt LIST Serializer ----------------------

class BookingReceiptSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title')

    class Meta:
        model = Booking
        fields = ['id', 'event_title', 'booked_at', 'total_amount', 'receipt_url']