from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.views import APIView
from django.utils.dateparse import parse_datetime
from django.db.models import Count
from .models import Room, Client, Booking
from .serializers import RoomSerializer, ClientSerializer, BookingSerializer


class RoomViewSet(viewsets.ModelViewSet):
    """
    Handles:
      - GET /rooms
      - POST /rooms
      - GET /rooms/{room_id}/bookings
      - GET /rooms/{room_id}/availability?time=...
      - GET /rooms/usage (custom action)
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    @action(detail=False, methods=['get'])
    def usage(self, request):
        """
        GET /rooms/usage
        Returns a stubbed percentage usage for each room.
        (In a real scenario, usage could be calculated based on total available time vs booked time.)
        """
        rooms = Room.objects.all()
        usage_data = []
        for room in rooms:
            total_bookings = room.bookings.count()
            # Dummy calculation: usage percentage based on bookings count
            percentage = min(total_bookings * 10, 100)
            usage_data.append({
                'room_id': room.id,
                'room_name': room.name,
                'usage_percentage': percentage
            })
        return Response(usage_data)

    @action(detail=True, methods=['get'], url_path='bookings')
    def room_bookings(self, request, pk=None):
        """
        GET /rooms/{room_id}/bookings
        List bookings for a specific room.
        """
        room = self.get_object()
        bookings = room.bookings.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='availability')
    def availability(self, request, pk=None):
        """
        GET /rooms/{room_id}/availability?time=...
        Checks if the room is free at the specified time.
        """
        room = self.get_object()
        time_str = request.query_params.get('time')
        if not time_str:
            return Response({"detail": "time query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        query_time = parse_datetime(time_str)
        if query_time is None:
            return Response({"detail": "Invalid datetime format"}, status=status.HTTP_400_BAD_REQUEST)
        # Check if any booking overlaps the specified time.
        overlapping = room.bookings.filter(start_time__lte=query_time, end_time__gte=query_time)
        available = not overlapping.exists()
        return Response({
            "room_id": room.id,
            "room_name": room.name,
            "available": available
        })


class BookingViewSet(viewsets.ModelViewSet):
    """
    Handles:
      - GET /bookings
      - POST /bookings
      - GET /bookings?client_id=...
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def list(self, request, *args, **kwargs):
        # If a client_id is provided, filter the bookings accordingly.
        client_id = request.query_params.get('client_id')
        if client_id:
            bookings = Booking.objects.filter(client__id=client_id)
        else:
            bookings = Booking.objects.all()
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)


class BookingOverlapsView(APIView):
    """
    GET /bookings/overlaps
    Returns a list of bookings that overlap in the same room.
    """

    def get(self, request):
        overlaps = []
        rooms = Room.objects.all()
        for room in rooms:
            bookings = list(room.bookings.order_by('start_time'))
            for i in range(len(bookings)):
                for j in range(i + 1, len(bookings)):
                    if bookings[i].end_time > bookings[j].start_time:
                        overlaps.append({
                            'room_id': room.id,
                            'room_name': room.name,
                            'booking1': BookingSerializer(bookings[i]).data,
                            'booking2': BookingSerializer(bookings[j]).data
                        })
        return Response(overlaps)


class ClientBookingsReport(APIView):
    """
    GET /clients/bookings
    Returns the number of bookings made by each client.
    """

    def get(self, request):
        report = Client.objects.annotate(booking_count=Count('bookings')).values('id', 'name', 'booking_count')
        return Response(report)


@api_view(['POST'])
def load_data(request):
    """
    POST /load-data
    Loads initial JSON data for rooms, clients, and bookings.
    Expected JSON structure:
    {
        "rooms": [ ... ],
        "clients": [ ... ],
        "bookings": [ ... ]
    }
    """

    data = request.data
    rooms_data = data.get('rooms', [])
    clients_data = data.get('clients', [])
    bookings_data = data.get('bookings', [])

    # Create rooms and store mapping from provided id to instance.
    room_map = {}
    for room_item in rooms_data:
        serializer = RoomSerializer(data=room_item)
        if serializer.is_valid():
            room = serializer.save()
            # Use provided id if available or the generated id.
            room_map[room_item.get('id', room.id)] = room
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create clients.
    client_map = {}
    for client_item in clients_data:
        serializer = ClientSerializer(data=client_item)
        if serializer.is_valid():
            client = serializer.save()
            client_map[client_item.get('id', client.id)] = client
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create bookings.
    for booking_item in bookings_data:
        room_id = booking_item.get('room_id')
        client_id = booking_item.get('client_id')
        if room_id not in room_map:
            return Response({"detail": f"Room id {room_id} not found"}, status=status.HTTP_400_BAD_REQUEST)
        if client_id not in client_map:
            return Response({"detail": f"Client id {client_id} not found"}, status=status.HTTP_400_BAD_REQUEST)
        # Map provided keys to model fields.
        booking_item['room'] = room_map[room_id].id
        booking_item['client'] = client_map[client_id].id
        booking_item.pop('room_id', None)
        booking_item.pop('client_id', None)
        serializer = BookingSerializer(data=booking_item)
        if serializer.is_valid():
            serializer.save()
        else:
            print('Booking Error:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Data loaded successfully"}, status=status.HTTP_201_CREATED)
