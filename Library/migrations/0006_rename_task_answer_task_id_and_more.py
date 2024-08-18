# Generated by Django 5.0.7 on 2024-08-13 15:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Library', '0005_rename_task_id_answer_task_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='task',
            new_name='task_id',
        ),
        migrations.RenameField(
            model_name='quizpool',
            old_name='creator',
            new_name='creator_id',
        ),
        migrations.RenameField(
            model_name='quiztask',
            old_name='creator',
            new_name='creator_id',
        ),
        migrations.RenameField(
            model_name='quiztask',
            old_name='pool',
            new_name='pool_id',
        ),
    ]
