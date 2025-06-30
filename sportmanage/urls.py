"""
URL configuration for sportmanage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from authenticate.views import custom_404_view  # adjust based on your app name

handler404 = custom_404_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authenticate.urls')),  # or whatever your app is named
    path('', include('booksystem.urls')),  # Now the base URL is /

]
