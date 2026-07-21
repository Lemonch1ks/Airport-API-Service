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
        read_only=True,
        slug_field="name",
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


class TicketSerializer(serializers.ModelSerializer):
    order = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="id",
    )
    flight = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="tickets",
    )

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )
    destination = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    
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
    route = serializers.SlugRelatedField(many=False, read_only=True, slug_field="id")
    airplane = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="id",
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
        )
