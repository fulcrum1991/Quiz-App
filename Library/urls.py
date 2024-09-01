from django.urls import path
from Library import views


urlpatterns = [
    path('', views.show_library, name='library'),
    path('library/', views.show_library, name='library'),
]

htmxpatterns = [
    # Quizpools
    path('library/create_quizpool', views.create_quizpool, name='create_quizpool'),
    path('library/delete_quizpool/<int:pool_id>', views.delete_quizpool, name='delete_quizpool'),
    path('library/change_quizpool_name/<int:pool_id>', views.change_quizpool_name, name='change_quizpool_name'),
    # Quiztasks
    # path('library/get_quiztasks/<int:pool_id>', views.get_quiztasks, name='get_quiztasks'),
    path('library/show_quiztasks/<int:pool_id>', views.show_quiztasks, name='show_quiztasks'),
    path('library/create_quiztask/<int:pool_id>', views.create_quiztask, name='create_quiztask'),
    path('library/delete_quiztask/<int:task_id>', views.delete_quiztask, name='delete_quiztask'),
    path('library/change_question/<int:task_id>', views.change_question, name='change_question'),
    # Answers
    path('library/show_answers/<int:task_id>', views.show_answers, name='show_answers'),
    path('library/create_answer/<int:task_id>', views.create_answer, name='create_answer'),
    path('library/edit_answer/<int:answer_id>', views.edit_answer, name='edit_answer'),
    path('library/delete_answer/<int:answer_id>', views.delete_answer, name='delete_answer'),
]

urlpatterns += htmxpatterns