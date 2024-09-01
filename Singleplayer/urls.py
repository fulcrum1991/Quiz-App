from django.urls import path
from Singleplayer import views


urlpatterns = [
    path('singleplayer', views.sp_overview, name='sp_overview'),
    path('singleplayer/sp_new_game', views.sp_new_game, name='sp_new_game'),
    path('singleplayer/sp_game/<int:game_id>', views.render_game, name='sp_game'),
    path('singleplayer/sp_resume_game', views.sp_resume_game, name='sp_resume_game'),
    path('singleplayer/sp_history', views.sp_history, name='sp_history'),
]

htmxpatterns = [
    path('singleplayer/show_lib_content/<int:pool_id>',
         views.show_lib_content, name='show_lib_content'),
    path('singleplayer/create_game/<int:pool_id>',
         views.create_game, name='create_game'),
    path('singleplayer/previous_task/<int:game_id>/<int:task_id>',
         views.render_quiztask_card, {'action': 'previous'}, name='previous_task'),
    path('singleplayer/next_task/<int:game_id>/<int:task_id>',
         views.render_quiztask_card, {'action': 'next'}, name='next_task'),
    path('singleplayer/sp_select_answer/<int:game_id>/<int:task_id>/<int:selected_answer_id>',
         views.render_quiztask_card, {'action': 'select'}, name='sp_select_answer'),
    path('singleplayer/evaluate_task/<int:game_id>/<int:task_id>/<int:selected_answer_id>',
         views.evaluate_task, name='evaluate_task'),
    path('singleplayer/game_result/<int:game_id>',
         views.render_game_result_card, name='game_result'),
    path('singleplayer/show_game_content/<int:game_id>',
         views.show_game_content, name='show_game_content'),
]

urlpatterns += htmxpatterns