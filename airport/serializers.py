from django.db import transaction
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


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


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


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.SlugRelatedField(
        many=False, read_only=False, slug_field="id", queryset=Route.objects.all().select_related()
    )

    airplane = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="id",
        queryset=Airplane.objects.all().select_related()
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
    crew = CrewSerializer(many=True, read_only=False)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


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
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "order",
            "flight",
        )

    def create(self, validated_data):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required to create a ticket."
            )

        with transaction.atomic():
            order = Order.objects.create(user=request.user)
            return Ticket.objects.create(order=order, **validated_data)
