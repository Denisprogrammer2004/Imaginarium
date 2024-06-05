from django.contrib import admin
from .models import Game, Player, Card, Round, PlayerCard

admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Card)
admin.site.register(Round)
admin.site.register(PlayerCard)
