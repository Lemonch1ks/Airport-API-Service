from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from airport.models import (
    Airport,
    Airplane,
    AirplaneType,
    Flight,
    Order,
    Ticket,
    Crew,
    Route,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "closest_big_city",
        )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
        )


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="name",
        queryset=AirplaneType.objects.all(),
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Crew.objects.all(),
                fields=("first_name", "last_name"),
            )
        ]


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="name",
        queryset=Airport.objects.all(),
    )
    destination = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="name",
        queryset=Airport.objects.all(),
    )

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
        )

    def validate(self, attrs):
        source = attrs.get("source", getattr(self.instance, "source", None))
        destination = attrs.get(
            "destination",
            getattr(self.instance, "destination", None),
        )

        if source and destination and source == destination:
            raise serializers.ValidationError(
                {"destination": "Destination airport must differ from source airport."}
            )

        return attrs


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="id",
        queryset=Route.objects.all().select_related(),
    )

    airplane = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="id",
        queryset=Airplane.objects.all().select_related(),
    )

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class FlightCreateSerializer(serializers.ModelSerializer):
    route = serializers.SlugRelatedField(
        many=False, read_only=False, slug_field="id", queryset=Route.objects.all()
    )
    airplane = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="id",
        queryset=Airplane.objects.all(),
    )
    crew = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Crew.objects.all(),
    )

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")

    def validate(self, attrs):
        route = attrs.get("route")

        departure_time = attrs.get(
            "departure_time",
            getattr(self.instance, "departure_time", None),
        )

        arrival_time = attrs.get(
            "arrival_time",
            getattr(self.instance, "arrival_time", None),
        )

        if route and route.source_id == route.destination_id:
            raise serializers.ValidationError(
                {"route": "Source airport must differ from destination airport."}
            )

        if departure_time and arrival_time and arrival_time <= departure_time:
            raise serializers.ValidationError(
                {"arrival_time": "Arrival time must be later than departure time."}
            )

        return attrs

    def create(self, validated_data):
        crew = validated_data.pop("crew", [])
        flight = Flight.objects.create(**validated_data)
        flight.crew.set(crew)
        return flight


class FlightDetailSerializer(serializers.ModelSerializer):
    crew = CrewSerializer(many=True, read_only=True)
    airplane = AirplaneSerializer(many=False, read_only=True)
    route = RouteSerializer(many=False, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "route",
            "crew",
            "airplane",
        )

    def validate(self, attrs):
        departure_time = attrs.get("departure_time")
        arrival_time = attrs.get("arrival_time")

        if departure_time >= arrival_time:
            raise serializers.ValidationError(
                {"time_error": "Departure time can't be later than arrival time."}
            )
        return attrs


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "order",
            "flight",
        )


class TicketCreateSerializer(serializers.ModelSerializer):
    flight = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.select_related("airplane").all(),
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
        )
        validators = []

    def validate(self, attrs):
        flight = attrs["flight"]
        row = attrs["row"]
        seat = attrs["seat"]
        airplane = flight.airplane
        errors = {}

        if row < 1:
            errors["row"] = "Row must be at least 1."
        elif row > airplane.rows:
            errors["row"] = f"Row must not exceed airplane rows ({airplane.rows})."

        if seat < 1:
            errors["seat"] = "Seat must be at least 1."
        elif seat > airplane.seats_in_row:
            errors["seat"] = (
                "Seat must not exceed airplane seats in row "
                f"({airplane.seats_in_row})."
            )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                {"user": "Authentication is required to create an order."}
            )

        if "user" in self.initial_data:
            raise serializers.ValidationError({"user": "This field is not accepted."})

        tickets = attrs.get("tickets", [])
        ticket_errors = [{} for _ in tickets]
        seen_tickets = {}

        for index, ticket in enumerate(tickets):
            key = (ticket["flight"].id, ticket["row"], ticket["seat"])
            previous_index = seen_tickets.get(key)

            if previous_index is not None:
                message = "Duplicate seat in this order request."
                ticket_errors[previous_index].setdefault("non_field_errors", []).append(
                    message
                )
                ticket_errors[index].setdefault("non_field_errors", []).append(message)
            else:
                seen_tickets[key] = index

            booked_seat = Ticket.objects.filter(
                flight=ticket["flight"],
                row=ticket["row"],
                seat=ticket["seat"],
            )

            if self.instance:
                booked_seat = booked_seat.exclude(order=self.instance)

            if booked_seat.exists():
                ticket_errors[index].setdefault("non_field_errors", []).append(
                    "This seat is already booked for this flight."
                )

        if any(ticket_errors):
            raise serializers.ValidationError({"tickets": ticket_errors})

        return attrs

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        request = self.context["request"]

        try:
            with transaction.atomic():
                order = Order.objects.create(user=request.user)
                Ticket.objects.bulk_create(
                    [Ticket(order=order, **ticket_data) for ticket_data in tickets_data]
                )

        except IntegrityError as exc:
            raise serializers.ValidationError(
                {"tickets": ["One or more selected seats have already been booked."]}
            ) from exc

        return order

    def update(self, instance, validated_data):
        tickets_data = validated_data.pop("tickets", None)

        if tickets_data is None:
            return instance

        try:
            with transaction.atomic():
                instance.tickets.all().delete()
                Ticket.objects.bulk_create(
                    [
                        Ticket(order=instance, **ticket_data)
                        for ticket_data in tickets_data
                    ]
                )

        except IntegrityError as exc:
            raise serializers.ValidationError(
                {"tickets": ["One or more selected seats have already been booked."]}
            ) from exc

        return instance
