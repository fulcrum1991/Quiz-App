from django.urls import path
from UserManagement import views


urlpatterns = [
    path('sign-up', views.sign_up, name='sign_up'),
    path('profile/', views.profile, name='profile'),
    path('delete_profile/', views.delete_profile, name='delete_profile'),
]