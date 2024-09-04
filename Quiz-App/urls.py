"""
URL configuration for Quiz-App project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include


urlpatterns = [
    # This is the default path for Django Admin. By visiting 'admin/' in the browser, you will see the
    # admin dashboard provided by Django.
    path('admin/', admin.site.urls),
    # This default path includes Django's built-in authentication URLs for login, logout,
    # password change, etc.
    path('', include('django.contrib.auth.urls')),
    # By including '*.urls', Django searches for urlpatterns in the apps' urls.py files.
    path('', include('Library.urls')),
    path('', include('UserManagement.urls')),
    path('', include('Singleplayer.urls')),
    #path('', include('Multiplayer.urls')),
]

