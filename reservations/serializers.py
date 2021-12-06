from rest_framework import serializers
from reservations.models import RoomCategory, Room, Booking, RoomBooking

class RoomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomCategory
        fields = ['id', 'price', 'name']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'number', 'category', 'capacity']

class BookingSerializer(serializers.ModelSerializer):
    room_numbers = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'name', 'surname', 'number_of_people', 'cost', 'room_ids', 'room_numbers', 'id', 'duration']

    def get_room_numbers(self, obj):
        return obj.get_room_numbers()

    def get_duration(self, obj):
        return (obj.end_date - obj.start_date).days

    def create(self, validated_data):
        rooms = validated_data.pop("rooms")
        booking = Booking.objects.create(**validated_data)
        booking.create_room_bookings(rooms)
        return booking

    def update(self, instance, validated_data):
        instance.start_date = validated_data["start_date"]
        instance.end_date = validated_data["end_date"]
        instance.name = validated_data["name"]
        instance.surname = validated_data["surname"]
        instance.number_of_people = validated_data["number_of_people"]
        instance.cost = validated_data["cost"]
        instance.room_ids = validated_data["room_ids"]
        
        if "rooms" in validated_data:
            rooms = validated_data.pop("rooms")
            room_bookings = RoomBooking.objects.filter(booking__id=instance.id).delete()
            instance.create_room_bookings(rooms)

        instance.save()
        return instance

class RoomBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomBooking
        fields = ['room', 'booking']