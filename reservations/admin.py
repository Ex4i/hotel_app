from django.contrib import admin

from .models import RoomCategory, Room, Booking, RoomBooking

admin.site.register(RoomCategory)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(RoomBooking)