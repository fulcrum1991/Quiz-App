from django.urls import path
from UserManagement import views


urlpatterns = [
    path('sign-up', views.sign_up, name='sign_up'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('accounts/profile_edit_form/', views.edit_profile, name='edit-profile'),
    path('accounts/delete-profile/', views.delete_profile, name='delete-profile'),
]