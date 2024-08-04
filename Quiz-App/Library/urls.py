from django.urls import path
from Library import views


urlpatterns = [
    path('', views.library, name='library'),
    path('library/', views.library, name='library'),
]

htmxpatterns = [
    path('library/get_quizpools', views.get_quizpools, name='get_quizpools'),
    path('library/create_quizpool', views.create_quizpool, name='create_quizpool'),
    path('library/delete_pool/<int:id>', views.delete_pool, name='delete_pool'),
    path('library/get_quiztasks/<int:pool_id>', views.get_quiztasks, name='get_quiztasks'),
    path('library/create_quiztask', views.create_quiztask, name='create_quiztask'),
    path('library/delete_task/<int:id>', views.delete_task, name='delete_task'),
    path('library/get_answers', views.get_answers, name='get_answers'),
]

urlpatterns += htmxpatterns