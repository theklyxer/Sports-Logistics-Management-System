from django.contrib import admin
from .models import Facility, Booking


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'facility', 'user', 'start_datetime', 'end_datetime', 'purpose')
    list_filter = ('purpose', 'start_datetime', 'facility')
    search_fields = ('user__username', 'facility__name', 'reason')
    ordering = ('-start_datetime',)
