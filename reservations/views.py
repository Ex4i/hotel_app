from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from reservations.serializers import RoomSerializer, RoomCategorySerializer, BookingSerializer, RoomBookingSerializer
from reservations.models import Room, RoomCategory, Booking, RoomBooking
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, GenericAPIView, RetrieveDestroyAPIView
from django.db import transaction
from datetime import datetime


### Rooms API ###

class RoomList(ListCreateAPIView):
    """
    List all rooms, or create a new room.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class RoomDetail(RetrieveUpdateDestroyAPIView):
    """
    Get, update or delete a selected room.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class RoomCategoryList(ListCreateAPIView):
    """
    List all room categories, or create a new room category.
    """
    queryset = RoomCategory.objects.all()
    serializer_class = RoomCategorySerializer

class RoomCategoryDetail(RetrieveUpdateDestroyAPIView):
    """
    Get, update or delete a selected room category.
    """
    queryset = RoomCategory.objects.all()
    serializer_class = RoomCategorySerializer


### Booking API ###

# Format room IDs from a string or list
def format_room_ids(room_ids):
    if type(room_ids) is str:
        room_ids = room_ids.replace(" ","").replace(";",",").split(',')
    return ",".join(str(room_id) for room_id in room_ids)

# Returns a list of Room objects for a list of room IDs.
fetch_rooms_by_ids = lambda room_ids: [Room.objects.get(pk=room_id) for room_id in room_ids.split(',')]

calculate_duration = lambda booking_data: (datetime.strptime(booking_data["end_date"], "%Y-%m-%d").date() - datetime.strptime(booking_data["start_date"], "%Y-%m-%d").date()).days

class BookingList(ListAPIView):
    """
    List all bookings or create a new one.
    When creating a new booking, please provide room_ids as a list or a string with ids separated by commas.
    This API endpoint allows for filtering results using GET request parameters. Use room_number parameter to filter by room number.
    Please note that the cost of booking is calculated on the server side, so the parameter will be ignored. 
    """
    serializer_class = BookingSerializer

    def get_queryset(self):
        queryset = Booking.objects.all()
        params = ['start_date', 'end_date', 'name', 'surname', 'number_of_people', 'cost']
        options = {}
        empty_options = []

        for param in params:
            options[param] = self.request.query_params.get(param)
        for option in options:
            if options[option] is None:
                empty_options.append(option)
        for option in empty_options:
            del(options[option])
        
        queryset = queryset.filter(**options)

        room_number = self.request.query_params.get('room_number')
        if room_number is not None:
            room_id = Room.objects.get(number=room_number).id
            room_bookings = list(RoomBooking.objects.filter(room=room_id))
            booking_ids = [x.booking.id for x in room_bookings]
            queryset = queryset.filter(pk__in=booking_ids)

        return queryset

    def post(self, request, format=None):

        booking_data = request.data.copy()
        booking_data["room_ids"] = format_room_ids(booking_data["room_ids"])
        rooms = fetch_rooms_by_ids(booking_data["room_ids"])
        try:
            Booking.validate_booking_data(booking_data, rooms)
            duration = calculate_duration(booking_data)
            booking_data["cost"] = Room.calculate_cost(rooms, duration)
        except Exception as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        print(booking_data["room_ids"])

        serializer = BookingSerializer(data=booking_data)
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save(rooms=rooms)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
class BookingDetail(RetrieveDestroyAPIView):
    """
    Retrieves, deletes or updates a specific booking.
    When updating a booking, please provide room_ids as a list or a string with ids separated by commas.
    Please note that the cost of booking is calculated on the server side, so the parameter will be ignored.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def put(self, request, pk, format=None):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response("Booking does not exist", status=status.HTTP_400_BAD_REQUEST)

        booking_data = request.data.copy()
        booking_data["room_ids"] = format_room_ids(booking_data["room_ids"])
        rooms = fetch_rooms_by_ids(booking_data["room_ids"])
        try:
            Booking.validate_booking_data(booking_data, rooms, booking.id)
            duration = calculate_duration(booking_data)
            booking_data["cost"] = Room.calculate_cost(rooms, duration)
        except Exception as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

        serializer = BookingSerializer(booking, data=booking_data)
        if serializer.is_valid():
            serializer.save(rooms=rooms)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookingDuration(GenericAPIView):
    """
    Returns a duration of a specific booking.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get(self, request, pk, format=None):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response("Booking does not exist", status=status.HTTP_400_BAD_REQUEST)
        response = {"duration":booking.get_duration()}
        return Response(response, status=status.HTTP_200_OK)

class BookingCost(GenericAPIView):
    """
    Returns a cost of a specific booking.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get(self, request, pk, format=None):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response("Booking does not exist", status=status.HTTP_400_BAD_REQUEST)
        response = {"cost":booking.cost}
        return Response(response, status=status.HTTP_200_OK)