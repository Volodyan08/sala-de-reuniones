from json import JSONDecodeError

from django.test import TestCase
from rest_framework import status
from rest_framework.test import RequestsClient

from meeting.models import Client  # using ORM for client creation when needed


HOST = 'http://localhost:8000/api'


# Sample payloads for testing
room_1_params = dict(
    name="Conference Room A",
    open_time="09:00:00",
    close_time="17:00:00",
    capacity=10
)

room_2_params = dict(
    name="Meeting Room B",
    open_time="08:00:00",
    close_time="20:00:00",
    capacity=5
)

booking_1_template = dict(
    start_time="2024-04-01T10:00:00Z",
    end_time="2024-04-01T11:00:00Z"
)

client_1_params = dict(
    name="Alice"
)

client_2_params = dict(
    name="Bob"
)


class CreateRoomTest(TestCase):
    def setUp(self):
        self.client_api = RequestsClient()
        self.url = HOST + '/rooms/'

    def test_room_creation(self):
        r = self.client_api.post(self.url, data=room_1_params)
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
        data = r.json()
        self.assertIn('id', data)
        self.assertTrue(isinstance(data['id'], int))
        self.assertEqual(data['name'], room_1_params['name'])
        self.assertEqual(data['open_time'], room_1_params['open_time'])
        self.assertEqual(data['close_time'], room_1_params['close_time'])
        self.assertEqual(data['capacity'], room_1_params['capacity'])


class ListRoomsTest(TestCase):
    def setUp(self):
        self.client_api = RequestsClient()
        self.url = HOST + '/rooms/'
        rooms = [room_1_params, room_2_params]
        self.created_rooms = []
        try:
            for room in rooms:
                response = self.client_api.post(self.url, data=room)
                self.created_rooms.append(response.json())
                self.created_rooms.append(response.json())
        except JSONDecodeError:
            self.fail('/rooms/ endpoint for POST request not implemented correctly')
        self.created_rooms.sort(key=lambda room: room['id'])

    def test_get_all_rooms(self):
        r = self.client_api.get(self.url)
        self.assertEquals(r.status_code, status.HTTP_200_OK)
        data = r.json()
        data.sort(key=lambda room: room['id'])
        self.assertListEqual(self.created_rooms, data)


class CreateBookingTest(TestCase):
    def setUp(self):
        self.client_api = RequestsClient()
        # Create a room via API
        room_url = HOST + '/rooms/'
        r = self.client_api.post(room_url, data=room_1_params)
        self.room = r.json()
        # Create a client using ORM (client endpoint is not exposed)
        self.client_obj = Client.objects.create(**client_1_params)
        self.url = HOST + '/bookings/'

    def test_booking_creation(self):
        booking_data = booking_1_template.copy()
        booking_data['room'] = self.room['id']
        booking_data['client'] = self.client_obj.id
        r = self.client_api.post(self.url, data=booking_data)
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
        data = r.json()
        self.assertIn('id', data)
        self.assertEqual(data['room'], self.room['id'])
        self.assertEqual(data['client'], self.client_obj.id)
        self.assertEqual(data['start_time'], booking_1_template['start_time'])
        self.assertEqual(data['end_time'], booking_1_template['end_time'])


class ListBookingsTest(TestCase):
    def setUp(self):
        self.client_api = RequestsClient()
        # Create a room
        room_url = HOST + '/rooms/'
        r = self.client_api.post(room_url, data=room_1_params)
        self.room = r.json()
        # Create a client
        self.client_obj = Client.objects.create(**client_1_params)
        # Create two bookings via API
        self.url = HOST + '/bookings/'
        bookings = [
            dict(
                room=self.room['id'],
                client=self.client_obj.id,
                start_time="2024-04-01T10:00:00Z",
                end_time="2024-04-01T11:00:00Z"
            ),
            dict(
                room=self.room['id'],
                client=self.client_obj.id,
                start_time="2024-04-01T12:00:00Z",
                end_time="2024-04-01T13:00:00Z"
            )
        ]
        self.created_bookings = []
        try:
            for booking in bookings:
                response = self.client_api.post(self.url, data=booking)
                self.created_bookings.append(response.json())
        except JSONDecodeError:
            self.fail('/bookings/ endpoint for POST request not implemented correctly')
        self.created_bookings.sort(key=lambda booking: booking['id'])

    def test_get_all_bookings(self):
        r = self.client_api.get(self.url)
        self.assertEquals(r.status_code, status.HTTP_200_OK)
        data = r.json()
        data.sort(key=lambda booking: booking['id'])
        self.assertListEqual(self.created_bookings, data)


class FilterBookingsByClientTest(TestCase):
    def setUp(self):
        self.client_api = RequestsClient()
        # Create a room
        room_url = HOST + '/rooms/'
        r = self.client_api.post(room_url, data=room_1_params)
        self.room = r.json()
        # Create two clients
        self.client1 = Client.objects.create(**client_1_params)
        self.client2 = Client.objects.create(**client_2_params)
        # Create bookings for both clients
        self.url = HOST + '/bookings/'
        bookings = [
            dict(
                room=self.room['id'],
                client=self.client1.id,
                start_time="2024-04-01T10:00:00Z",
                end_time="2024-04-01T11:00:00Z"
            ),
            dict(
                room=self.room['id'],
                client=self.client2.id,
                start_time="2024-04-01T12:00:00Z",
                end_time="2024-04-01T13:00:00Z"
            )
        ]
        self.created_bookings = []
        try:
            for booking in bookings:
                response = self.client_api.post(self.url, data=booking)
                self.created_bookings.append(response.json())
        except JSONDecodeError:
            self.fail('/bookings/ endpoint for POST request not implemented correctly')
        self.created_bookings.sort(key=lambda booking: booking['id'])

    def test_filter_bookings_by_client(self):
        url = HOST + '/bookings/?client_id={}'.format(self.client1.id)
        r = self.client_api.get(url)
        self.assertEquals(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['client'], self.client1.id)


class RoomAvailabilityTest(TestCase):
    def setUp(self):
        self.client_api = RequestsClient()
        # Create a room
        room_url = HOST + '/rooms/'
        r = self.client_api.post(room_url, data=room_1_params)
        self.room = r.json()
        # Create a client
        self.client_obj = Client.objects.create(**client_1_params)
        # Create a booking that makes the room unavailable at a specific time
        booking_url = HOST + '/bookings/'
        booking_data = dict(
            room=self.room['id'],
            client=self.client_obj.id,
            start_time="2024-04-01T10:00:00Z",
            end_time="2024-04-01T11:00:00Z"
        )
        self.client_api.post(booking_url, data=booking_data)

    def test_room_availability(self):
        # Test time during an active booking
        url = HOST + f"/rooms/{self.room['id']}/availability/?time=2024-04-01T10:30:00Z"
        r = self.client_api.get(url)
        self.assertEquals(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertFalse(data.get("available"))

        # Test time when room is free
        url = HOST + f"/rooms/{self.room['id']}/availability/?time=2024-04-01T11:30:00Z"
        r = self.client_api.get(url)
        self.assertEquals(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertTrue(data.get("available"))


class BookingOverlapsTest(TestCase):
    def setUp(self):
        self.client_api = RequestsClient()
        # Create a room
        room_url = HOST + '/rooms/'
        r = self.client_api.post(room_url, data=room_1_params)
        self.room = r.json()
        # Create a client
        self.client_obj = Client.objects.create(**client_1_params)
        # Create overlapping bookings
        self.url = HOST + '/bookings/'
        bookings = [
            dict(
                room=self.room['id'],
                client=self.client_obj.id,
                start_time="2024-04-01T10:00:00Z",
                end_time="2024-04-01T11:00:00Z"
            ),
            dict(
                room=self.room['id'],
                client=self.client_obj.id,
                start_time="2024-04-01T10:30:00Z",
                end_time="2024-04-01T11:30:00Z"
            )
        ]
        self.created_bookings = []
        try:
            for booking in bookings:
                response = self.client_api.post(self.url, data=booking)
                self.created_bookings.append(response.json())
        except JSONDecodeError:
            self.fail('/bookings/ endpoint for POST request not implemented correctly')
        self.created_bookings.sort(key=lambda booking: booking['id'])

    def test_get_overlapping_bookings(self):
        url = HOST + '/bookings/overlaps/'
        r = self.client_api.get(url)
        self.assertEquals(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertTrue(len(data) >= 1)


class LoadDataTest(TestCase):
    def setUp(self):
        self.client_api = RequestsClient()
        self.url = HOST + '/load-data/'
        self.load_data_payload = {
            "rooms": [
                {
                    "id": 100,
                    "name": "Conference Room X",
                    "open_time": "09:00:00",
                    "close_time": "17:00:00",
                    "capacity": 20
                }
            ],
            "clients": [
                {
                    "id": 100,
                    "name": "Charlie"
                }
            ],
            "bookings": [
                {
                    "room_id": 100,
                    "client_id": 100,
                    "start_time": "2024-04-01T14:00:00Z",
                    "end_time": "2024-04-01T15:00:00Z"
                }
            ]
        }

    def test_load_data(self):
        r = self.client_api.post(self.url, data=self.load_data_payload)
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
        data = r.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Data loaded successfully")
