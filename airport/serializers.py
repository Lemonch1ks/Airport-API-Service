from rest_framework import serializers

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
