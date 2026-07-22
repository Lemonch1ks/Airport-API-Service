from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    OrderViewSet,
    TicketViewSet,
    RouteViewSet,
    FlightViewSet,
    CrewViewSet,
)

router = routers.DefaultRouter()

router.register("airports", AirportViewSet)
router.register("airplanes/types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("crews", CrewViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
