# Generated by Django 5.0.6 on 2024-06-05 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_game_current_player'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='association',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
