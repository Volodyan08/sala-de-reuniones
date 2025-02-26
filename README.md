# Meeting Room API ("La Sala de Reuniones Caliente")

This project is a RESTful API for managing meeting rooms in a coworking space. The API enables clients to view available meeting rooms, make and list bookings, and obtain various reports on usage and reservations.

### **HOT** 
Meeting Room API already available at https://meeting-room.vintila.dev//api/. You can make requests to the API using the interface described in the meeting_room_api.yaml file or use test_api.py to make requests to the API.

## Table of Contents

- [Overview](#overview)
- [Data Model](#data-model)
- [API Endpoints](#api-endpoints)
- [Initial Data Loading](#initial-data-loading)
- [Technologies](#technologies)
- [Setup and Installation](#setup-and-installation)
- [Running the Service](#running-the-service)
- [Deployment](#deployment)
- [Documentation & Report](#documentation--report)

## Overview

In a coworking environment, multiple meeting rooms are shared among clients. This API allows for:
- Coordinating room usage and reservations.
- Querying real-time availability.
- Generating reports such as room usage percentages and client reservation statistics.

## Data Model

The initial data is provided via a JSON file with the following structure:

- **rooms:** List of available meeting rooms including:
  - `id`: Unique room identifier.
  - `open_time`: Opening time.
  - `close_time`: Closing time.
  - `capacity`: Room capacity.

- **clients:** List of clients eligible to make reservations:
  - `id`: Unique client identifier.
  - `name`: Client name.

- **bookings:** List of bookings with:
  - `room_id`: Identifier of the room.
  - `client_id`: Identifier of the client.
  - `start_time`: Booking start time.
  - `end_time`: Booking end time.

## API Endpoints

The API will support the following endpoints:

1. **List Rooms:**  
   `GET /rooms`  
   Returns a list of all meeting rooms.

2. **List Bookings:**  
   `GET /bookings`  
   Returns a list of all bookings.

3. **Create Booking:**  
   `POST /bookings`  
   Creates a new booking by specifying room, client, start time, and end time.

4. **List Client Bookings:**  
   `GET /bookings?client_id={client_id}`  
   Returns bookings for a specific client.

5. **List Room Bookings:**  
   `GET /rooms/{room_id}/bookings`  
   Returns bookings for a specific room.

6. **Add New Room:**  
   `POST /rooms`  
   Adds a new meeting room with the necessary details.

7. **Room Usage Percentage:**  
   `GET /rooms/usage`  
   Returns the percentage of usage for each room.

8. **Bookings per Client:**  
   `GET /clients/bookings`  
   Returns the number of bookings made by each client.

9. **Room Availability:**  
   `GET /rooms/{room_id}/availability?time={time}`  
   Checks if a specific room is available at a given time.

10. **Overlapping Bookings:**  
    `GET /bookings/overlaps`  
    Lists bookings that overlap in the same room.

11. **Load Initial Data:**  
    `POST /load-data`  
    Loads initial JSON data into the database.

## Initial Data Loading

An example JSON file with initial data is provided. Use the `/load-data` endpoint to populate the database.

## Technologies

- **Programming Language:** Python
- **Web Framework:** Django
- **Database:** PostgreSQL
- **Containerization:** Docker and Docker Compose

## Setup and Installation

1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Create a .env file with the following environment variables:
   - `SECRET_KEY`: Django secret key.
   - Database settings:
     - `POSTGRES_DB`
     - `POSTGRES_USER`
     - `POSTGRES_PASSWORD`
     - `POSTGRES_HOST`
     - `POSTGRES_PORT`
4. Run the docker-compose file using `docker-compose up`.
5. Run the migrations using `docker-compose exec web python manage.py migrate`.


## Running the Service

- To start the development server, run:
    ```
    docker-compose up
    docker-compose exec web python manage.py makemigrations
    docker-compose exec web python manage.py migrate
    ```
- The API will be available at `http://localhost:8000`.
- Fill the database with initial data using the `/load-data` endpoint. Can use corresponding function from test_api.py.
- interface described in the meeting_room_api.yaml file.
