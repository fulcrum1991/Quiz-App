from django.urls import path
from . import views

app_name = 'multiplayer'

urlpatterns = [
    path('multiplayer/', views.mp_overview, name='mp_overview'),
    path('new/', views.mp_new_game, name='mp_new_game'),
    path('lobby/<int:game_id>/', views.mp_lobby, name='mp_lobby'),
    path('join/<int:pool_id>/', views.join_game, name='join_game'),
    path('game/<int:game_id>/', views.render_game, name='render_game'),
    path('game/<int:game_id>/task/<int:task_id>/<str:action>/', views.render_quiztask_card, name='render_quiztask_card'),
    path('game/<int:game_id>/evaluate/<int:task_id>/<int:selected_answer_id>/', views.evaluate_task, name='evaluate_task'),
    path('game/<int:game_id>/result/', views.mp_game_result, name='mp_game_result'),
    path('resume/', views.mp_resume_game, name='mp_resume_game'),
    path('history/', views.mp_history, name='mp_history'),
    path('content/', views.show_game_content, name='show_game_content'),
    path('lobby-content/<int:game_id>/', views.mp_lobby_content, name='mp_lobby_content'),
    path('game/<int:game_id>/quiztask_status/', views.quiztask_status, name='quiztask_status'),
    path('check_game_status/<int:game_id>/', views.check_game_status, name='check_game_status'),
]

