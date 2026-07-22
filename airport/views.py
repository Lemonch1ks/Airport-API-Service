from django.db.models import Q
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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
    FlightCreateSerializer,
    OrderCreateSerializer,
)


def _query_param_values(query_params, *param_names):
    values = []
    for param_name in param_names:
        for value in query_params.getlist(param_name):
            values.extend(
                part.strip() for part in value.split(",") if part.strip()
            )
    return values


def _filter_by_ids(queryset, query_params, field_name, *param_names):
    values = _query_param_values(query_params, *param_names)

    if not values:
        return queryset

    try:
        ids = [int(value) for value in values]
    except ValueError:
        return queryset.none()

    return queryset.filter(**{f"{field_name}__in": ids})


def _filter_by_airport(queryset, query_params, relation_name, *param_names):
    values = _query_param_values(query_params, *param_names)

    if not values:
        return queryset

    query = Q()
    for value in values:
        if value.isdecimal():
            query |= Q(**{f"{relation_name}_id": int(value)})

        query |= (
            Q(**{f"{relation_name}__name__icontains": value})
            | Q(**{f"{relation_name}__closest_big_city__icontains": value})
        )

    return queryset.filter(query)


def _filter_by_datetime(queryset, query_params, field_name, *param_names):
    values = _query_param_values(query_params, *param_names)

    if not values:
        return queryset

    query = Q()
    for value in values:
        date = parse_date(value)

        if date:
            query |= Q(**{f"{field_name}__date": date})
            continue

        date_time = parse_datetime(value)

        if date_time:
            query |= Q(**{field_name: date_time})

    if not query:
        return queryset.none()

    return queryset.filter(query)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all().select_related()
    serializer_class = AirportSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related()
    serializer_class = AirplaneSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [
        IsAdminOrReadOnly,
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
        IsAuthenticated,
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
        if self.action in ("create", "update", "partial_update"):
            return OrderCreateSerializer
        return OrderSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params

        queryset = _filter_by_airport(queryset, query_params, "source", "source")
        queryset = _filter_by_airport(
            queryset,
            query_params,
            "destination",
            "destination",
        )

        return queryset


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related(
            "route__source",
            "route__destination",
            "airplane__airplane_type",
        )
        .prefetch_related("crew")
    )
    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params

        queryset = _filter_by_ids(
            queryset,
            query_params,
            "route_id",
            "route",
            "route_id",
        )
        queryset = _filter_by_ids(
            queryset,
            query_params,
            "airplane_id",
            "airplane",
            "airplane_id",
        )
        queryset = _filter_by_airport(
            queryset,
            query_params,
            "route__source",
            "source",
        )
        queryset = _filter_by_airport(
            queryset,
            query_params,
            "route__destination",
            "destination",
        )
        queryset = _filter_by_datetime(
            queryset,
            query_params,
            "departure_time",
            "departure_date",
            "departure_time",
        )
        queryset = _filter_by_datetime(
            queryset,
            query_params,
            "arrival_time",
            "arrival_date",
            "arrival_time",
        )

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FlightDetailSerializer
        if self.action == "create":
            return FlightCreateSerializer
        return FlightSerializer
