# Generated by Django 5.0.8 on 2024-08-29 18:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Library', '0011_rename_task_id_answer_task_and_more'),
        ('Singleplayer', '0007_rename_game_id_spgame_contains_quiztask_game_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='spgame_contains_quiztask',
            name='selected_answer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Library.answer'),
        ),
        migrations.AlterField(
            model_name='spgame_contains_quiztask',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Library.quiztask'),
        ),
    ]
