import requests
import json

BASE_URL = "https://meeting-room.vintila.dev/api"


def load_data():
    url = f"{BASE_URL}/load-data/"
    with open("load-data.json", "r") as f:
        data = json.load(f)
    response = requests.post(url, json=data)
    print("Load Data Response:", response.status_code)
    print(response.json())


def list_rooms():
    url = f"{BASE_URL}/rooms/"
    response = requests.get(url)
    print("List Rooms Response:", response.status_code)
    print(response.json())


def list_bookings():
    url = f"{BASE_URL}/bookings/"
    response = requests.get(url)
    print("List Bookings Response:", response.status_code)
    print(response.json())


def create_booking():
    url = f"{BASE_URL}/bookings/"
    # Sample booking data
    booking_data = {
        "room": 1,
        "client": 2,
        "start_time": "2024-04-01T12:00:00Z",
        "end_time": "2024-04-01T13:00:00Z"
    }
    response = requests.post(url, json=booking_data)
    print("Create Booking Response:", response.status_code)
    print(response.json())


if __name__ == "__main__":
    print("Testing load_data:")
    load_data()

    print("\nTesting list_rooms:")
    list_rooms()

    print("\nTesting list_bookings:")
    list_bookings()

    print("\nTesting create_booking:")
    create_booking()
