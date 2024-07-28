from django.urls import path, include
from Library import views


urlpatterns = [
    path('', views.library, name='library'),
    path('library', views.library, name='library'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('create-quiztask', views.create_quiztask, name='create-quiztask'),
]