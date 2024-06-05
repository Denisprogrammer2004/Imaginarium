# Generated by Django 5.0.6 on 2024-06-04 19:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_alter_card_game'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='current_player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='game.player'),
        ),
    ]
