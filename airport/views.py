from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from airport.permissions import IsAdminOrReadOnly

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Order,
    Ticket,
    Route,
    Flight,
)

from airport.serializers import (
    AirportSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    CrewSerializer,
    OrderSerializer,
    TicketSerializer,
    RouteSerializer,
    FlightSerializer,
    FlightDetailSerializer,
    TicketCreateSerializer,
    FlightCreateSerializer,
)

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [
        AllowAny,
    ]


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [
        AllowAny,
    ]


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = [
        AllowAny,
    ]


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [
        AllowAny,
    ]


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [
        AllowAny,
    ]

    def get_serializer_class(self):
        if self.action == "create":
            return TicketCreateSerializer
        return TicketSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [
        AllowAny,
    ]


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    permission_classes = [
        AllowAny,
    ]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FlightDetailSerializer
        if self.action == "create":
            return FlightCreateSerializer
        return FlightSerializer
