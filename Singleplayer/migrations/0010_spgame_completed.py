# Generated by Django 5.0.8 on 2024-09-01 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Singleplayer', '0009_spgame_correct_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='spgame',
            name='completed',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
