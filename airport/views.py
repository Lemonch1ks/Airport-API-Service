from rest_framework import viewsets, mixins

from airport.models import Airport
from airport.serializers import (
    AirportSerializer,

)

class AirportViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
