from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
import json
from .models import CustomUser
from booksystem.models import Booking 
import re
import jwt
import random


User = get_user_model()

# ────────────────────────────────────────────────────────
# Helper: Extract user & role from cookie JWT
# ────────────────────────────────────────────────────────
def get_user_and_role(request):
    token = request.COOKIES.get('access')
    if not token:
        return None, None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=payload.get('user_id'))
        return user, user.role
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
        return None, None


# ────────────────────────────────────────────────────────
# Public: Homepage
# ────────────────────────────────────────────────────────
def index(request):
    return render(request, 'index.html')


# ────────────────────────────────────────────────────────
# Signup View
# ────────────────────────────────────────────────────────
OTP_STORE = {}

class RequestOTPAPI(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        age = data.get('age')

        if not all([username, email, phone, age]):
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(username=username).exists():
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Email must match a previously used one
        if CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'Phone number already used, Use a different phone number'}, status=status.HTTP_400_BAD_REQUEST)

        # Phone must also match a previously used one
        if CustomUser.objects.filter(phone=phone).exists():
            return Response({'error': 'Phone number already used, Use a different phone number'}, status=status.HTTP_400_BAD_REQUEST)

        # Age validation
        try:
            age = int(age)
            if age < 18 or age > 70:
                return Response({'error': 'Age must be between 18 and 70.'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Age must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(100000, 999999))
        OTP_STORE[username] = {
            "otp": otp,
            "data": data,
            "expires_at": timezone.now() + timezone.timedelta(minutes=10)
        }

        # Send OTP email
        try:
            send_mail(
                subject="Your OTP Code",
                message=f"Your OTP code is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False
            )
        except Exception as e:
            return Response({'error': f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)


class VerifyOTPAPI(APIView):
    def post(self, request):
        username = request.data.get('username')
        otp = request.data.get('otp')

        if not username or not otp:
            return Response({'error': 'Username and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        record = OTP_STORE.get(username)
        if not record:
            return Response({'error': 'No OTP request found.'}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() > record['expires_at']:
            del OTP_STORE[username]
            return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)

        if otp != record['otp']:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user now
        user_data = record['data']
        password = user_data.get('password')
        phone = user_data.get('phone')
        age = user_data.get('age')
        email = user_data.get('email')

        # Role assignment
        if re.match(r"^[a-zA-Z]", email):
            role = "staff"
        elif re.match(r"^\d", email):
            role = "student"
        else:
            role = "student"

        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            phone=phone,
            age=age,
            email=email,
            role=role
        )

        # Clear OTP record
        del OTP_STORE[username]

        return Response({'message': 'Signup successful', 'role': role}, status=status.HTTP_201_CREATED)



# ────────────────────────────────────────────────────────
# Login via JWT with Cookies
# ────────────────────────────────────────────────────────
@method_decorator(csrf_exempt, name='dispatch')
class CookieTokenLogin(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({'message': 'Logged in with cookies'}, status=status.HTTP_200_OK)
        response.set_cookie(
            key='access',
            value=access_token,
            httponly=True,
            samesite='Lax',
            secure=False,
            max_age=3600
        )
        response.set_cookie(
            key='refresh',
            value=str(refresh),
            httponly=True,
            samesite='Lax',
            secure=False,
            max_age=7 * 24 * 3600
        )
        return response


# ────────────────────────────────────────────────────────
# Logout (clear cookies)
# ────────────────────────────────────────────────────────
@api_view(['POST'])
def logout_cookie(request):
    response = Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    response.delete_cookie('access')
    response.delete_cookie('refresh')
    return redirect('/')


# ────────────────────────────────────────────────────────
# DRF Authenticated User Info (fallback to cookie parsing)
# ────────────────────────────────────────────────────────
@api_view(['GET'])
def user_info(request):
    user, role = get_user_and_role(request)
    if not user:
        return Response({'error': 'Unauthenticated'}, status=401)

    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': role
    })


# ────────────────────────────────────────────────────────
# Student Profile View
# ────────────────────────────────────────────────────────
def student_profile_view(request):
    user, role = get_user_and_role(request)
    if not user or role != 'student':
        return redirect('/')

    student_bookings = Booking.objects.filter(user=user).order_by('-start_datetime')
    return render(request, 'student_profile.html', {
        'user': user,
        'bookings': student_bookings,
    })


# ────────────────────────────────────────────────────────
# Staff Profile View
# ────────────────────────────────────────────────────────
def staff_profile_view(request):
    user, role = get_user_and_role(request)
    if not user or role != 'staff':
        return redirect('/')

    staff_blocked_slots = Booking.objects.filter(user=user, purpose='block').order_by('-start_datetime')
    return render(request, 'staff_profile.html', {
        'user': user,
        'blocked_slots': staff_blocked_slots,
    })



# ────────────────────────────────────────────────────────
# 404 Not Found Handler
# ────────────────────────────────────────────────────────
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)
