from django.db import models

class Game(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    current_player = models.ForeignKey('Player', related_name='+', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=255)
    game = models.ForeignKey('Game', related_name='players', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    is_bot = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Round(models.Model):
    game = models.ForeignKey('Game', related_name='rounds', on_delete=models.CASCADE)
    current_card = models.ForeignKey('Card', related_name='+', on_delete=models.SET_NULL, null=True)
    association = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Round {self.id} of {self.game.name}"

class Card(models.Model):
    description = models.CharField(max_length=255)
    image = models.ImageField(upload_to='cards/')
    game = models.ForeignKey('Game', related_name='cards', on_delete=models.CASCADE, null=True, blank=True)
    round = models.ForeignKey('Round', related_name='cards', on_delete=models.CASCADE, null=True, blank=True)  # новое поле

    def __str__(self):
        return self.description

class PlayerCard(models.Model):
    player = models.ForeignKey('Player', related_name='player_cards', on_delete=models.CASCADE)
    card = models.ForeignKey('Card', related_name='playercard', on_delete=models.CASCADE)  # Обратите внимание на изменение related_name
    in_hand = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.player.name} - {self.card.description}"
