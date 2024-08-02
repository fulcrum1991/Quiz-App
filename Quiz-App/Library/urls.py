from django.urls import path
from Library import views
from Library.views import sign_up

urlpatterns = [
    path('', views.library, name='library'),
    path('library', views.library, name='library'),
    path('create-quiztask', views.create_quiztask, name='create-quiztask'),

    path('sign-up/', sign_up, name='sign_up'),
    path('profile/', views.profile, name='profile'),
    path('delete_profile/', views.delete_profile, name='delete_profile'),
]