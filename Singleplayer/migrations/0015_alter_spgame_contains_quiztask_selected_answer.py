# Generated by Django 5.0.8 on 2024-09-04 11:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Library', '0013_alter_answer_answer_alter_answer_creator_and_more'),
        ('Singleplayer', '0014_alter_spgame_contains_quiztask_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spgame_contains_quiztask',
            name='selected_answer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Library.answer'),
        ),
    ]
