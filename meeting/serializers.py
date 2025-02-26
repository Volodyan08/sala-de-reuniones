from rest_framework import serializers
from .models import Room, Client, Booking


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def validate(self, data):
        # Here you can add custom validation.
        # For example, to optionally enforce that bookings do not overlap,
        # you might check for existing bookings for the same room.
        # if 'room' in data and 'start_time' in data and 'end_time' in data:
        #     room = data['room']
        #     start_time = data['start_time']
        #     end_time = data['end_time']
        #     if Booking.objects.filter(room=room, start_time__lt=end_time, end_time__gt=start_time).exists():
        #         raise serializers.ValidationError('Booking overlaps with existing booking.')
        return data
