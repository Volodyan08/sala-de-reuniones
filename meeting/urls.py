from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, BookingViewSet, ClientBookingsReport, BookingOverlapsView, load_data

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('clients/bookings/', ClientBookingsReport.as_view(), name='client-bookings-report'),
    path('bookings/overlaps/', BookingOverlapsView.as_view(), name='booking-overlaps'),
    path('load-data/', load_data, name='load-data'),
]
