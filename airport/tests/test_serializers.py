from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from django.utils import timezone

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

class SerializerTests(TestCase):

    def setUp(self):

        self.admin_client = APIClient()
        self.user_client = APIClient()

        self.admin = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin"
        )
        self.admin_client.force_authenticate(user=self.admin)

        self.user = get_user_model().objects.create_user(
            email="123@123.com", password="123"
        )
        self.user_client.force_authenticate(user=self.user)

        self.crew = Crew.objects.create(first_name="John", last_name="Doe")
        self.airplane_type = AirplaneType.objects.create(name="Airplane")
        self.airport1 = Airport.objects.create(
            name="airport1", closest_big_city="London"
        )
        self.airport2 = Airport.objects.create(
            name="airport2", closest_big_city="new_york"
        )
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
            departure_time=timezone.make_aware(datetime(2026, 7, 23, 12, 30)),
            arrival_time=timezone.make_aware(datetime(2026, 7, 23, 15, 30)),
        )
        self.flight.crew.add(self.crew)

        self.order = Order.objects.create(
            user=get_user_model().objects.create_user(
                email="12@12.com",
                password="12",
            )
        )

        self.Ticket = Ticket.objects.create(
            row=12, seat=5, flight=self.flight, order=self.order
        )

    def test_create_order(self):

        payload = {
            "tickets": [
                {
                    "flight": self.flight.pk,
                    "row": 1,
                    "seat": 1,
                }
            ]
        }

        response = self.user_client.post(
            "/api/airport/orders/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(Ticket.objects.count(), 2)
        self.assertTrue(Order.objects.filter(user=self.user).exists())
