from django.test import TestCase
from reservations.models import Room, RoomCategory, Booking, RoomBooking
from reservations.serializers import BookingSerializer
from datetime import datetime, timedelta

# Create your tests here.

class RoomTestCase(TestCase):
    def setUp(self):
        cat_A = RoomCategory.objects.create(id="A",price=400,name="A")
        cat_B = RoomCategory.objects.create(id="B",price=100,name="B")
        room_1 = Room.objects.create(number=12,category=cat_A,capacity=5)
        room_2 = Room.objects.create(number=23,category=cat_B,capacity=4)

    def test_capacity(self):
        """Test checking capacity of the rooms"""
        rooms = []
        rooms.append(Room.objects.get(pk=1))
        rooms.append(Room.objects.get(pk=2))        

        self.assertEqual(Room.check_rooms_capacity(rooms,10), False)
        self.assertEqual(Room.check_rooms_capacity(rooms,9), True)

    def test_cost(self):
        """Test checking cost of the rooms"""
        rooms = []
        rooms.append(Room.objects.get(pk=1))
        rooms.append(Room.objects.get(pk=2))        

        self.assertEqual(rooms[0].get_cost(), 400)
        self.assertEqual(Room.calculate_cost(rooms, 2), 1000)

    def test_availability(self):
        """Test checking availability of the rooms"""
        test_date = datetime.today().date() + timedelta(days=10)
        rooms = []
        rooms.append(Room.objects.get(pk=1))
        rooms.append(Room.objects.get(pk=2))
        test_date = datetime.today().date() + timedelta(days=10)
        
        book1 = Booking.objects.create(start_date=test_date,end_date=(test_date + timedelta(days=1)),name="x",surname="x",room_ids=rooms[0].id,number_of_people=2,cost=500)
        book2 = Booking.objects.create(start_date=test_date,end_date=(test_date + timedelta(days=1)),name="x",surname="x",room_ids=rooms[1].id,number_of_people=2,cost=500)
        RoomBooking.objects.create(room=rooms[0], booking=book1)
        RoomBooking.objects.create(room=rooms[1], booking=book2)

        # check availability for a new booking
        self.assertEqual(rooms[0].is_available(test_date, test_date + timedelta(days=1)), False)
        self.assertEqual(rooms[0].is_available(test_date + timedelta(days=1), test_date + timedelta(days=2)), True)
        self.assertEqual(Room.check_rooms_availability(rooms, test_date, test_date + timedelta(days=1)), False)
        self.assertEqual(Room.check_rooms_availability(rooms, test_date + timedelta(days=1), test_date + timedelta(days=2)), True)

        # check availability for a booking being modified, excluding current booking
        self.assertEqual(rooms[0].is_available(test_date, test_date + timedelta(days=1), book1.id), True)
        self.assertEqual(rooms[0].is_available(test_date, test_date + timedelta(days=1), book2.id), False)


    def test_negative_capacity(self):
        """Check that creation of a room with negative capacity fails"""
        cat_A = RoomCategory.objects.get(id="A")
        self.assertRaises(Exception, Room.objects.create(number=3,category=cat_A,capacity=-1))


class RoomCategoryTestCase(TestCase):

    def test_creation(self):
        """Test creation of room categories"""
        self.assertEqual(RoomCategory.objects.create(id="A",price=100,name="Test2").id, "A")
        self.assertRaises(Exception, RoomCategory.objects.create(id="B",price=-100,name="Test2"))


class BookingTestCase(TestCase):
    def setUp(self):
        cat_A = RoomCategory.objects.create(id="A",price=400,name="A")
        cat_B = RoomCategory.objects.create(id="B",price=100,name="B")
        room_1 = Room.objects.create(number=12,category=cat_A,capacity=5)
        room_2 = Room.objects.create(number=23,category=cat_B,capacity=4)
        

    def test_date_correctness_check(self):
        """Test the is_date_range_correct function"""
        test_date = datetime.today().date()
        # correct date in the future
        self.assertEqual(Booking.is_date_range_correct(str(test_date), str(test_date + timedelta(days=1))), True) 
        # start date in the past
        self.assertEqual(Booking.is_date_range_correct(str(test_date - timedelta(days=1)), str(test_date + timedelta(days=1))), False)
        # start date after end date
        self.assertEqual(Booking.is_date_range_correct(str(test_date + timedelta(days=1)), str(test_date)), False)
        # booking shorter than one day
        self.assertEqual(Booking.is_date_range_correct(str(test_date + timedelta(days=1)), str(test_date + timedelta(days=1))), False) 

    def test_booking_creation(self):
        """Test booking creation"""
        test_date = datetime.today().date() + timedelta(days=10)
        room_ids_1 = "1"
        room_ids_2 = "1,2"
        rooms_1 = [Room.objects.get(pk=room_id) for room_id in room_ids_1.split(',')]
        rooms_2 = [Room.objects.get(pk=room_id) for room_id in room_ids_2.split(',')]

        book1 = Booking.objects.create(start_date=test_date,end_date=(test_date + timedelta(days=10)),name="x",surname="x",room_ids=room_ids_1,number_of_people=2,cost=500)
        test_date += timedelta(days=10)
        book2 = Booking.objects.create(start_date=test_date,end_date=(test_date + timedelta(days=10)),name="x",surname="x",room_ids=room_ids_2,number_of_people=2,cost=500)

        book1.create_room_bookings(rooms_1)
        book1_roombookings = RoomBooking.objects.filter(booking=book1)
        self.assertEqual(len(book1_roombookings),1)
        book2.create_room_bookings(rooms_2)
        book2_roombookings = RoomBooking.objects.filter(booking=book2)
        self.assertEqual(len(book2_roombookings),2)

    def test_get_room_numbers_and_duration(self):
        """Test miscellaneous class functions"""
        test_date = datetime.today().date() + timedelta(days=10)
        room_ids = "1,2"
        rooms = [Room.objects.get(pk=room_id) for room_id in room_ids.split(',')]

        book = Booking.objects.create(start_date=test_date,end_date=(test_date + timedelta(days=10)),name="x",surname="x",room_ids=room_ids,number_of_people=2,cost=500)
        book.create_room_bookings(rooms)

        self.assertEqual(book.get_room_numbers(), [12,23])
        self.assertEqual(book.get_duration(), 10)


class BookingSerializerTestCase(TestCase):
    def setUp(self):
        cat_A = RoomCategory.objects.create(id="A",price=400,name="A")
        cat_B = RoomCategory.objects.create(id="B",price=100,name="B")
        room_1 = Room.objects.create(number=12,category=cat_A,capacity=5)
        room_2 = Room.objects.create(number=23,category=cat_B,capacity=4)
        

    def test_serializer(self):
        """Tests parsing data and RoomBookings creations"""
        test_date = datetime.today().date()

        request_data = {
            "start_date": test_date,
            "end_date": test_date + timedelta(days=10),
            "name": "Test",
            "surname": "Testing",
            "number_of_people": 2 ,
            "cost": 0,
            "room_ids": "1,2"
        }

        rooms = [Room.objects.get(pk=room_id) for room_id in request_data["room_ids"].split(',')]
        serializer = BookingSerializer(data=request_data)
        self.assertEqual(serializer.is_valid(), True)
        booking = serializer.save(rooms=rooms)

        self.assertEqual(len(RoomBooking.objects.filter(booking=booking)),2)