from rest_framework import viewsets, mixins

from airport.permissions import IsAdminOrReadOnly

from airport.models import Airport

from airport.serializers import (
    AirportSerializer,

)

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminOrReadOnly,]
