# Generated by Django 5.0.8 on 2024-08-24 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Singleplayer', '0003_alter_spgame_completed_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spgame',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
