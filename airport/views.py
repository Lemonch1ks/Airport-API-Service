from rest_framework import viewsets
from rest_framework.permissions import AllowAny

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
    OrderCreateSerializer,
    TicketSerializer,
    RouteSerializer,
    FlightSerializer,
    FlightDetailSerializer,
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
    queryset = Airplane.objects.all().select_related()
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


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [
        AllowAny,
    ]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related(
                "order__user",
                "flight__airplane",
                "flight__route",
            )
            .prefetch_related("flight__crew")
        )

        user = self.request.user

        if user.is_staff:
            return queryset

        if user.is_authenticated:
            return queryset.filter(order__user=user)

        return queryset.none()


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [
        AllowAny,
    ]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("user")
            .prefetch_related(
                "tickets__flight__airplane",
                "tickets__flight__route",
                "tickets__flight__crew",
            )
        )

        user = self.request.user

        if user.is_staff:
            return queryset

        if user.is_authenticated:
            return queryset.filter(user=user)

        return queryset.none()

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related()
    serializer_class = RouteSerializer
    permission_classes = [
        AllowAny,
    ]


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().select_related()
    permission_classes = [
        AllowAny,
    ]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FlightDetailSerializer
        if self.action == "create":
            return FlightCreateSerializer
        return FlightSerializer
