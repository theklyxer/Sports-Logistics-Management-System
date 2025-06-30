from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    staff_dashboard,
    student_dashboard,
    facility_list,
    calendar_status,
    slots_for_day,
    book_slot,
    add_facility,
    block_slot,
    all_facilities_calendar_status,
    FacilityViewSet,
    BookingViewSet,
)

router = DefaultRouter()
router.register(r'facilities', FacilityViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('dashboard/student/', student_dashboard, name='student_dashboard'),
    path('dashboard/staff/', staff_dashboard, name='staff_dashboard'),
    path('facilities/', facility_list, name='facility_list'),
    path('facilities/create/', add_facility, name='add_facility'),
    path('calendar/<int:facility_id>/', calendar_status, name='calendar_status'),
    path('book/', book_slot, name='book_slot'),  # only used for custom booking logic
    path('slots/<int:facility_id>/', slots_for_day, name='slots_for_day'),
    path('block/', block_slot, name='block_slot'),
    path('api/all-calendar/', all_facilities_calendar_status, name='all_facilities_calendar_status'),
    path('api/', include(router.urls)),  # this handles all CRUD for bookings and facilities
]
