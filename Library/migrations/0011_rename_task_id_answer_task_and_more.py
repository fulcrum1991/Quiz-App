# Generated by Django 5.0.8 on 2024-08-23 12:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Library', '0010_rename_task_answer_task_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='task_id',
            new_name='task',
        ),
        migrations.RenameField(
            model_name='quizpool',
            old_name='creator_id',
            new_name='creator',
        ),
        migrations.RenameField(
            model_name='quiztask',
            old_name='creator_id',
            new_name='creator',
        ),
        migrations.RenameField(
            model_name='quiztask',
            old_name='pool_id',
            new_name='pool',
        ),
    ]
