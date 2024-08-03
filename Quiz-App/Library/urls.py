from django.urls import path
from Library import views


urlpatterns = [
    path('', views.library, name='library'),
    path('library', views.library, name='library'),
    path('create-quiztask', views.create_quiztask, name='create-quiztask'),

]