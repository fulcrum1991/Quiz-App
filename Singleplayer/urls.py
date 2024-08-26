from django.urls import path
from Singleplayer import views


urlpatterns = [
    path('singleplayer', views.sp_overview, name='sp_overview'),
    path('singleplayer/sp_new_game', views.sp_new_game, name='sp_new_game'),
    path('singleplayer/show_lib_content/<int:pool_id>', views.show_lib_content, name='show_lib_content'),

    path('singleplayer/sp_resume_game', views.sp_resume_game, name='sp_resume_game'),
    path('singleplayer/sp_history', views.sp_history, name='sp_history'),
]

htmxpatterns = [
    # Quizpools
    path('singleplayer/create_game/<int:pool_id>', views.create_game, name='create_game'),
    path('singleplayer/evaluate_task', views.evaluate_task, name='evaluate_task'),
    path('singleplayer/previous_task/<int:game_id>/<int:task_id>', views.previous_task, name='previous_task'),
    path('singleplayer/next_task/<int:game_id>/<int:task_id>', views.next_task, name='next_task'),
    path('singleplayer/sp_check_answer/<int:game_id>/<int:answer_id>', views.check_answer, name='check_answer'),
]

urlpatterns += htmxpatterns