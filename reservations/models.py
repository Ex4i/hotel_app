from django.db import models
from django.core.validators import MinValueValidator
from decimal import *
from datetime import datetime
from functools import reduce

class RoomCategory(models.Model):
    id = models.CharField(primary_key=True, max_length=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Room(models.Model):
    number = models.PositiveIntegerField(unique=True)
    category = models.ForeignKey(RoomCategory, on_delete=models.DO_NOTHING)
    capacity = models.PositiveIntegerField()
    def __str__(self):
        return str(self.number)

    def is_available(self, start_date, end_date, booking_id=None):
        room_bookings = RoomBooking.objects.filter(room__id=self.id, booking__end_date__gt=start_date, booking__start_date__lt=end_date)
        if booking_id is not None:
            room_bookings = room_bookings.exclude(booking__id=booking_id)
        return False if len(room_bookings) > 0 else True

    def check_rooms_availability(rooms, start_date, end_date, booking_id=None):
        for room in rooms:
            if not room.is_available(start_date, end_date, booking_id):
                return False
        return True

    def check_rooms_capacity(rooms, people):
        capacity = reduce(lambda x, room: x+room.capacity, rooms, 0)
        return True if capacity >= int(people) else False

    def calculate_cost(rooms):
        cost = 0
        for room in rooms:
            room_category = RoomCategory.objects.get(pk=room.category)
            cost += room_category.price
        return cost

class Booking(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    room_ids = models.CharField(max_length=100)
    number_of_people = models.PositiveIntegerField() 
    cost = models.PositiveIntegerField()
    def __str__(self):
        return self.name + " " + self.surname
            
    def is_date_range_correct(start_date, end_date):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        return True if start_date >= datetime.now().date() and end_date > start_date else False

    def create_room_bookings(self, rooms):
        for room in rooms:
            room_booking = RoomBooking(room=room, booking=self)
            room_booking.save()

    def validate_booking_data(booking_data, rooms, booking_id=None):
        if not Booking.is_date_range_correct(booking_data["start_date"], booking_data["end_date"]):
            raise Exception("Incorrect date range")
        if not Room.check_rooms_availability(rooms, booking_data["start_date"], booking_data["end_date"], booking_id):
            raise Exception("Rooms booked already for given date range")
        if not Room.check_rooms_capacity(rooms, booking_data["number_of_people"]):
            raise Exception("Rooms have insufficient capacity")
        return True

    def get_room_numbers(self):
        return [room_booking.room.number for room_booking in RoomBooking.objects.filter(booking=self.id)]

    def get_duration(self):
        return (self.end_date - self.start_date).days


class RoomBooking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.room) + str(self.booking)