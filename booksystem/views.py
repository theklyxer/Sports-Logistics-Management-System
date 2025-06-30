from datetime import datetime, timedelta, date, timezone, time
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.core.mail import send_mail,EmailMessage
from rest_framework import viewsets, status
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.exceptions import ValidationError
from booksystem.models import Facility, Booking
from booksystem.serializers import FacilitySerializer, BookingSerializer
from authenticate.models import CustomUser
import jwt
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime
User = get_user_model()

# ─── HELPER ─────────────────────────────────────────────
def get_user_and_role(request):
    token = request.COOKIES.get('access')
    if not token:
        return None, None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=payload.get("user_id"))
        return user, user.role
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
        return None, None

def get_user_from_access_token(request):
    token = request.COOKIES.get('access')
    if not token:
        return None, None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        return user, user.role
    except Exception:
        return None, None

# ─── DASHBOARDS ─────────────────────────────────────────
def student_dashboard(request):
    user, role = get_user_from_access_token(request)
    if not user:
        return redirect('/')
    if role != 'student':
        return redirect('/')
    return render(request, 'student_dashboard.html')

def staff_dashboard(request):
    user, role = get_user_from_access_token(request)
    if not user:
        return redirect('/')
    if role != 'staff':
        return redirect('/')
    return render(request, 'staff_dashboard.html')


# ─── FACILITY LISTING ───────────────────────────────────
@api_view(['GET'])
def facility_list(request):
    facilities = Facility.objects.all().values('id', 'name')
    return Response(list(facilities))

# ─── STAFF: ADD NEW FACILITY ───────────────────────────
@api_view(['POST'])
def add_facility(request):
    user, role = get_user_and_role(request)
    if not user:
        return Response({'error': 'Unauthenticated'}, status=401)
    if role != 'staff':
        return Response({'error': 'Only staff can add facilities'}, status=403)

    name = request.data.get('name')
    if not name:
        return Response({'error': 'Facility name required'}, status=400)

    Facility.objects.create(name=name)
    return Response({'message': 'Facility created'})

# ─── CALENDAR STATUS (FOR STUDENT UI) ──────────────────
@api_view(['GET'])
def calendar_status(request, facility_id):
    today = datetime.now().date()
    summary = []
    for i in range(14):
        current_date = today + timedelta(days=i)

        bookings = Booking.objects.filter(
            facility_id=facility_id,
            start_datetime__date__lte=current_date,
            end_datetime__date__gte=current_date
        ).values('id', 'start_datetime', 'end_datetime', 'purpose', 'reason')


        total_booked_minutes = 0

        for booking in bookings:
            # Strip timezone info if accidentally present
            start = booking['start_datetime'].replace(tzinfo=None)
            end = booking['end_datetime'].replace(tzinfo=None)

            # Define effective boundaries (naive UTC)
            day_start = datetime.combine(current_date, time(hour=5, minute=0))
            day_end = datetime.combine(current_date, time(hour=22, minute=59, second=59, microsecond=999999))

            # Compute effective booking time
            effective_start = max(start, day_start)
            effective_end = min(end, day_end)

            if effective_start < effective_end and effective_start.date() == current_date:
                duration = effective_end - effective_start
                total_booked_minutes += duration.total_seconds() / 60

        total_booked_hours = total_booked_minutes / 60


        status = 'green'
        if total_booked_hours >= 17:
            status = 'red'
        elif total_booked_hours >= 12:
            status = 'orange'
        summary.append({'date': current_date, 'status': status})
    return Response(summary)


# ─── GET HOURLY AVAILABILITY ───────────────────────────
@api_view(['GET'])
def slots_for_day(request, facility_id):
    date_str = request.GET.get('date')
    if not date_str:
        return Response({'error': 'Missing date param'}, status=400)
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_of_day = datetime.combine(date_obj, datetime.min.time())
        end_of_day = datetime.combine(date_obj, datetime.max.time())
    except ValueError:
        return Response({'error': 'Invalid date format'}, status=400)

    bookings = Booking.objects.filter(
        facility_id=facility_id,
        start_datetime__lt=end_of_day,
        end_datetime__gt=start_of_day
    ).values('id', 'start_datetime', 'end_datetime', 'purpose', 'reason', 'user_id')

    all_hours = set(range(5, 23))
    booked_intervals = []

    for booking in bookings:
        start_time_on_day = max(booking['start_datetime'], start_of_day)
        end_time_on_day = min(booking['end_datetime'], end_of_day)

        start_hour = start_time_on_day.hour if start_time_on_day.date() == date_obj else 5
        end_hour = end_time_on_day.hour if end_time_on_day.date() == date_obj else 23

        if booking['end_datetime'].date() > date_obj:
            end_hour = 23
        if booking['start_datetime'].date() < date_obj:
            start_hour = 5

        booked_intervals.append((start_hour, end_hour))

    availability = []
    for h in sorted(list(all_hours)):
        is_available = True
        for booked_start, booked_end in booked_intervals:
            if h >= booked_start and h < booked_end:
                is_available = False
                break
        availability.append({'hour': h, 'available': is_available})

    return Response(availability)

# ─── STUDENT BOOK SLOT ─────────────────────────────────
@api_view(['POST'])
def book_slot(request):
    user, role = get_user_and_role(request)
    if not user:
        return Response({'error': 'Unauthenticated'}, status=401)
    if role != 'student':
        return Response({'error': 'Only students can book slots'}, status=403)

    try:
        facility_id = request.data['facility_id']
        start_datetime_str = request.data['start_datetime']
        end_datetime_str = request.data['end_datetime']

        start_datetime = datetime.fromisoformat(start_datetime_str.replace('Z', ''))
        end_datetime = datetime.fromisoformat(end_datetime_str.replace('Z', ''))

        start_datetime = start_datetime.replace(minute=0, second=0, microsecond=0)
        end_datetime = end_datetime.replace(minute=0, second=0, microsecond=0)

    except (KeyError, ValueError):
        return Response({'error': 'Invalid datetime format or missing input'}, status=400)

    conflicts = Booking.objects.filter(
        facility_id=facility_id,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime
    )
    if conflicts.exists():
        return Response({'error': 'Time slot conflict'}, status=409)

    booking = Booking.objects.create(
        user=user,
        facility_id=facility_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        purpose='booking'
    )

    html_message = render_to_string('email/booking_confirmation.html', {'booking': booking})
    email = EmailMessage(
        subject='Booking Confirmation',
        body=html_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    email.content_subtype = 'html'
    try:
        email.send()
    except Exception as e:
        print("Email sending failed:", e)

    return Response({'message': 'Booking successful'})


# ─── STAFF: BLOCK SLOT ─────────────────────────────────
@api_view(['POST'])
def block_slot(request):
    user, role = get_user_and_role(request)
    if not user:
        return Response({'error': 'Unauthenticated'}, status=401)
    if role != 'staff':
        return Response({'error': 'Only staff can block slots'}, status=403)

    try:
        facility_id = request.data['facility_id']
        start_datetime_str = request.data['start_datetime']
        end_datetime_str = request.data['end_datetime']
        reason = request.data.get('reason', 'Blocked by staff')

        start_datetime = datetime.fromisoformat(start_datetime_str.replace('Z', ''))
        end_datetime = datetime.fromisoformat(end_datetime_str.replace('Z', ''))

        start_datetime = start_datetime.replace(minute=0, second=0, microsecond=0)
        end_datetime = end_datetime.replace(minute=0, second=0, microsecond=0)

    except (KeyError, ValueError):
        return Response({'error': 'Invalid datetime format or missing input'}, status=400)

    # Fetch conflicting bookings/blocks
    conflicts = Booking.objects.filter(
        facility_id=facility_id,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime
    )

    # Store emails of users whose bookings will be deleted
    affected_users = []

    for conflict in conflicts:
        # Only notify users with purpose 'booking'
        if conflict.purpose == 'booking' and conflict.user and conflict.user.email:
            affected_users.append((conflict.user.email, conflict))
        conflict.delete()

    # Send notification to affected users
    for email, booking in affected_users:
        html_message = render_to_string('email/booking_cancelled_by_staff.html', {
            'booking': booking,
            'reason': reason
        })
        email_obj = EmailMessage(
            subject='Booking Cancelled Due to Staff Block',
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )
        email_obj.content_subtype = 'html'
        try:
            email_obj.send()
        except Exception as e:
            print(f"Failed to send cancellation email to {email}: {e}")

    # Now create the blocking slot
    Booking.objects.create(
        user=user,
        facility_id=facility_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        purpose='block',
        reason=reason
    )
    return Response({'message': 'Slot blocked successfully. Conflicting bookings were cancelled.'})


# ─── ADMIN: ALL FACILITIES CALENDAR STATUS ─────────────
@api_view(['GET'])
def all_facilities_calendar_status(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not start_date_str or not end_date_str:
        return Response({'error': 'Missing start_date or end_date parameters'}, status=400)

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    all_events = []
    bookings = Booking.objects.filter(
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime
    ).select_related('facility', 'user')

    for booking in bookings:
        event = {
            'id': booking.id,
            'facility_id': booking.facility.id,
            'facility_name': booking.facility.name,
            'start': booking.start_datetime.isoformat(),
            'end': booking.end_datetime.isoformat(),
            'purpose': booking.purpose,
            'reason': booking.reason,
            'user_username': booking.user.username if booking.user else None,
            'title': f"Booking by {booking.user.username}" if booking.purpose == 'booking' and booking.user else (f"Blocked: {booking.reason}" if booking.purpose == 'block' else ""),
        }
        all_events.append(event)

    daily_summary = {}
    current_date = start_date
    while current_date <= end_date:
        daily_summary[current_date.isoformat()] = {
            'date': current_date.isoformat(),
            'booking_count': 0,
            'block_count': 0,
            'total_events': 0,
            'events': []
        }
        current_date += timedelta(days=1)

    for event in all_events:
        event_start_date = datetime.fromisoformat(event['start']).date()
        event_end_date = datetime.fromisoformat(event['end']).date()

        d = event_start_date
        while d <= event_end_date:
            if start_date <= d <= end_date:
                date_key = d.isoformat()
                if date_key in daily_summary:
                    if event['purpose'] == 'booking':
                        daily_summary[date_key]['booking_count'] += 1
                    elif event['purpose'] == 'block':
                        daily_summary[date_key]['block_count'] += 1
                    daily_summary[date_key]['total_events'] += 1
                    daily_summary[date_key]['events'].append(event)
            d += timedelta(days=1)

    final_summary = []
    for date_key in sorted(daily_summary.keys()):
        summary = daily_summary[date_key]
        total = summary['total_events']
        color = '#28a745'
        if total >= 5:
            color = '#ffc107'
        if total >= 10:
            color = '#dc3545'

        final_summary.append({
            'date': summary['date'],
            'color': color,
            'title': f"Events: {total}",
            'events': summary['events']
        })

    return Response(final_summary)



@api_view(['PUT', 'PATCH'])
def edit_facility(request, facility_id):
    user, role = get_user_and_role(request)
    if not user:
        return Response({'error': 'Unauthenticated'}, status=401)
    if role != 'staff':
        return Response({'error': 'Only staff can edit facilities'}, status=403)

    try:
        facility = Facility.objects.get(id=facility_id)
    except Facility.DoesNotExist:
        return Response({'error': 'Facility not found'}, status=404)

    name = request.data.get('name')
    if not name:
        return Response({'error': 'Facility name required'}, status=400)
    
    facility.name = name
    facility.save()
    return Response({'message': 'Facility updated successfully'})

@api_view(['DELETE'])
def delete_facility(request, facility_id):
    user, role = get_user_and_role(request)
    if not user:
        return Response({'error': 'Unauthenticated'}, status=401)
    if role != 'staff':
        return Response({'error': 'Only staff can delete facilities'}, status=403)

    try:
        facility = Facility.objects.get(id=facility_id)
    except Facility.DoesNotExist:
        return Response({'error': 'Facility not found'}, status=404)

    facility.delete()
    return Response({'message': 'Facility deleted successfully'})

class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer

    def get_permissions(self):
        return []


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_permissions(self):
        return []

    def get_queryset(self):
        user, _ = get_user_from_access_token(self.request)
        if user:
            if user.role in ['admin', 'staff']:
                return Booking.objects.all()
            return Booking.objects.filter(user=user)
        return Booking.objects.none()

    def perform_update(self, serializer):
        user, role = get_user_from_access_token(self.request)
        if not user:
            raise ValidationError({'error': 'Unauthenticated'})

        old_booking = self.get_object()

        new_start = serializer.validated_data.get('start_datetime', old_booking.start_datetime)
        new_end = serializer.validated_data.get('end_datetime', old_booking.end_datetime)
        facility = serializer.validated_data.get('facility', old_booking.facility)

        conflicts = Booking.objects.filter(
            facility=facility,
            start_datetime__lt=new_end,
            end_datetime__gt=new_start
        ).exclude(id=old_booking.id)

        if conflicts.exists():
            raise ValidationError({'error': 'Booking time conflicts with an existing booking.'})

        booking = serializer.save()
        self.send_booking_notification(booking, 'updated', old_booking)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user, _ = get_user_from_access_token(request)
        if not user:
            return Response({'error': 'Unauthenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        self.send_booking_notification(instance, 'cancelled')
        instance.delete()
        return Response({'message': 'Booking cancelled successfully.'}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        booking = Booking.objects.get(id=response.data['id'])
        self.send_booking_notification(booking, 'created')
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return response

    def send_booking_notification(self, booking, action_type, old_booking=None):
        user_email = booking.user.email
        facility_name = booking.facility.name
        start_time = booking.start_datetime.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        end_time = booking.end_datetime.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        if action_type == 'created':
            subject = 'Booking Confirmation'
            html_message = render_to_string('email/booking_confirmation.html', {'booking': booking})
        elif action_type == 'updated':
            subject = 'Booking Updated'
            old_start_time = old_booking.start_datetime.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            old_end_time = old_booking.end_datetime.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            html_message = render_to_string('email/booking_updated.html', {
                'booking': booking,
                'old_start': old_start_time,
                'old_end': old_end_time,
            })
        elif action_type == 'cancelled':
            subject = 'Booking Cancellation'
            html_message = render_to_string('email/booking_cancellation.html', {'booking': booking})
        else:
            return

        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER  # Update if needed

        send_mail(subject, plain_message, from_email, [user_email], html_message=html_message)

    @action(detail=False, methods=['get'], url_path='availability')
    def get_availability(self, request):
        facility_id = request.query_params.get('facility_id')
        date_str = request.query_params.get('date')

        if not facility_id or not date_str:
            return Response({'error': 'Facility ID and date are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            facility = Facility.objects.get(id=facility_id)
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Facility.DoesNotExist:
            return Response({'error': 'Facility not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        bookings = Booking.objects.filter(
            facility=facility,
            start_datetime__date=date
        ).order_by('start_datetime')

        booked_slots = [{
            'start': b.start_datetime.astimezone(timezone.utc).isoformat(),
            'end': b.end_datetime.astimezone(timezone.utc).isoformat()
        } for b in bookings]

        return Response({
            'facility': facility.name,
            'date': date_str,
            'booked_slots': booked_slots
        })
