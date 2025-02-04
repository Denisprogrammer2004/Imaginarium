# Generated by Django 5.0.6 on 2024-05-28 13:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_player_is_bot'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_hand', models.BooleanField(default=True)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='game.card')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_cards', to='game.player')),
            ],
        ),
    ]
