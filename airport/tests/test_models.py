from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase
from django.db import IntegrityError, transaction
from airport.models import (
    Crew,
    AirplaneType,
    Airport,
    Airplane,
    Route,
    Flight,
    Ticket,
    Order,
)

class Modelest(TestCase):

    def setUp(self):
        self.crew = Crew.objects.create(first_name="John", last_name="Doe")
        self.airplane_type = AirplaneType.objects.create(name="Airplane")
        self.airport1 = Airport.objects.create(name="airport1", closest_big_city="London")
        self.airport2 = Airport.objects.create(name="airport2", closest_big_city="new_york")
        self.airplane = Airplane.objects.create(
            name="airplane", airplane_type=self.airplane_type, rows=12, seats_in_row=3
        )
        self.route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=10,
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.make_aware(
                datetime(2026, 7, 23, 12, 30)
            ),
            arrival_time=timezone.make_aware(
                datetime(2026, 7, 23, 15, 30)
            )
        )
        self.flight.crew.add(self.crew)

        self.order=Order.objects.create(
            user=get_user_model().objects.create_user(
                email="123@123.com",
                password="123",
            )
        )

        self.Ticket = Ticket.objects.create(
            row=12,
            seat=5,
            flight=self.flight,
            order=self.order
        )

    def test_crew_str(self):
        self.assertEqual(str(self.crew), "John Doe")

    def test_airplane_type_str(self):
        self.assertEqual(str(self.airplane_type), "Airplane")

    def test_airport_str(self):
        self.assertEqual(str(self.airport1), "airport1")
        self.assertEqual(str(self.airport2), "airport2")

    def test_airplane_str(self):
        self.assertEqual(str(self.airplane), "airplane")

    def test_route_str(self):
        self.assertEqual(str(self.route), "airport1 -> airport2")

    def test_flight_str(self):
        self.assertEqual(
            str(self.flight),
            f"id:{self.flight.pk} route:{self.flight.route.source} -> {self.flight.route.destination}"
        )

    def test_crew_first_and_last_name_must_be_unique_together(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Crew.objects.create(
                    first_name="John",
                    last_name="Doe",
                )

    def test_ticket_flight_row_and_seats_must_be_unique_together(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Ticket.objects.create(
                    row=12,
                    seat=5,
                    flight=self.flight,
                    order=self.order
                )
