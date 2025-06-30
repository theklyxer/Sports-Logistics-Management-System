# myapp/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import index, CookieTokenLogin, logout_cookie,user_info, student_profile_view, staff_profile_view,RequestOTPAPI, VerifyOTPAPI

urlpatterns = [
    path('',index,name='index'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/login-cookie/', CookieTokenLogin.as_view(), name='cookie_login'),
    path('api/logout-cookie/', logout_cookie, name='cookie_logout'),
    path('api/current-user/', user_info, name='current_user_info'),
    path('profile/student/', student_profile_view, name='student_profile'),
    path('profile/staff/', staff_profile_view, name='staff_profile'),
    path('signup/request-otp/', RequestOTPAPI.as_view()),
    path('signup/verify-otp/', VerifyOTPAPI.as_view()),   
]

