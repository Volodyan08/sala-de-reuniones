from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100)
    open_time = models.TimeField()
    close_time = models.TimeField()
    capacity = models.IntegerField()

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.room.name} booked by {self.client.name} from {self.start_time} to {self.end_time}"
