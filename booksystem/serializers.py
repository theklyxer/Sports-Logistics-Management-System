# booksystem/serializers.py

from rest_framework import serializers
from .models import Facility, Booking

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def validate(self, data):
        # Get fields for validation
        facility = data.get('facility', getattr(self.instance, 'facility', None))
        start_dt = data.get('start_datetime', getattr(self.instance, 'start_datetime', None))
        end_dt = data.get('end_datetime', getattr(self.instance, 'end_datetime', None))

        if not facility or not start_dt or not end_dt:
            raise serializers.ValidationError("Facility, start_datetime, and end_datetime are required.")

        if start_dt >= end_dt:
            raise serializers.ValidationError("End time must be after start time.")

        # Check overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            facility=facility,
            start_datetime__lt=end_dt,
            end_datetime__gt=start_dt
        )
        if self.instance:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)

        if overlapping_bookings.exists():
            raise serializers.ValidationError("This time slot is already booked.")

        return data
