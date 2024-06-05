from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Game, Player, Card, Round, PlayerCard
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.db import transaction
import random
import logging

logger = logging.getLogger(__name__)

def main_menu(request):
    return render(request, 'game/main_menu.html')


def select_game(request):
    return render(request, 'game/select_game.html')


def create_game(request):
    if request.method == 'POST':
        bots_enabled = request.POST.get('bots_enabled') == 'on'
        players_count = int(request.POST.get('players_count'))
        game_type = request.POST.get('game_type')
        my_invite_code = request.POST.get('my_invite_code')

        try:
            with transaction.atomic():
                # создание новой игры
                game = Game.objects.create(name=my_invite_code)
                print(f'Game created: {game}')

                # добавление игрока
                player = Player.objects.create(name='Player 1', game=game, is_bot=False)
                print(f'Player created: {player}')
                players = [player]

                # добавление ботов, если они включены
                if bots_enabled:
                    for i in range(players_count - 1):  # Добавляем (players_count - 1) ботов
                        bot = Player.objects.create(name=f'Bot {i + 1}', game=game, is_bot=True)
                        players.append(bot)
                        print(f'Bot created: {bot}')

                # первый игрок - текущий игрок
                game.current_player = player
                game.save()

                # Раздача карточек
                cards = list(Card.objects.all())  # Получаем все карточки
                total_cards_needed = 6 * len(players)
                print(f'Total cards needed: {total_cards_needed}')
                print(f'Available cards: {len(cards)}')

                # Проверка, достаточно ли карточек
                if len(cards) < total_cards_needed:
                    print('Not enough cards, distributing available cards')
                    while cards:
                        for player in players:
                            if not cards:
                                break
                            card = cards.pop(0)
                            card.game = game  # Связываем карточку с игрой
                            card.save()
                            PlayerCard.objects.create(player=player, card=card)
                            print(f'Card {card.description} assigned to {player.name}')
                else:
                    print('Enough cards, distributing 6 cards to each player')
                    for player in players:
                        random_cards = random.sample(cards, 6)
                        for card in random_cards:
                            card.game = game  # Связываем карточку с игрой
                            card.save()
                            PlayerCard.objects.create(player=player, card=card)
                            print(f'Card {card.description} assigned to {player.name}')
                            cards.remove(card)  # Удаляем разданные карточки из списка

        except Exception as e:
            print(f'Error: {e}')
            return redirect('select_game')  # или другой подходящий маршрут

        return redirect(reverse('game_board') + f'?game_id={game.id}')

    player_range = range(4, 8)  # Пример диапазона для количества игроков
    return render(request, 'game/create_game.html', {'player_range': player_range})


def join_game(request):
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code')
        return render(request, 'game/game_board.html', {'invite_code': invite_code})
    return render(request, 'game/join_game.html')


def game_board(request):
    game_id = request.GET.get('game_id')
    game = get_object_or_404(Game, id=game_id)
    logger.info(f'Game loaded: {game}')

    current_round = game.rounds.filter(active=True).first()
    if not current_round:
        current_round = Round.objects.create(game=game, active=True)
        logger.info(f'New round created: {current_round}')

    player = game.current_player
    if not player:
        logger.error('No current player found in the game')
        return redirect('select_game')

    player_cards = PlayerCard.objects.filter(player=player, in_hand=True)

    # PlayerCard объекты, выбранные в текущем раунде
    selected_player_cards = PlayerCard.objects.filter(
        card__game=game,
        card__round=current_round,
        in_hand=False
    ).distinct()

    # карточки, выбранные ботами в текущем раунде
    bot_selected_player_cards = PlayerCard.objects.filter(
        card__game=game,
        card__round=current_round,
        in_hand=False,
        player__is_bot=True
    ).distinct()

    # Получаем сами карточки из PlayerCard
    selected_cards = [player_card.card for player_card in selected_player_cards]
    bot_selected_cards = [player_card.card for player_card in bot_selected_player_cards]

    # Отладочные выводы
    logger.info(f'Selected cards: {[card.description for card in selected_cards]}')
    logger.info(f'Bot selected cards: {[card.description for card in bot_selected_cards]}')

    return render(request, 'game/game_board.html', {
        'game': game,
        'current_round': current_round,
        'player_cards': player_cards,
        'selected_cards': selected_cards,
        'bot_selected_cards': bot_selected_cards,
        'players': game.players.all(),
        'current_player': player
    })

def choose_card(request, card_id):
    if request.method == 'POST':
        card = get_object_or_404(Card, id=card_id)
        player_card = get_object_or_404(PlayerCard, card=card)
        player_card.in_hand = False
        player_card.save()

        if card.game:
            current_round = card.game.rounds.filter(active=True).first()
            if current_round:
                if not PlayerCard.objects.filter(player__game=card.game, in_hand=True).exists():
                    current_round.active = False
                    current_round.save()
                    Round.objects.create(game=card.game, active=True)
                # Переход хода к след. игроку
                players = list(card.game.players.all())
                current_player_index = players.index(card.game.current_player)
                next_player_index = (current_player_index + 1) % len(players)
                card.game.current_player = players[next_player_index]
                card.game.save()

                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'failed', 'error': 'No active round found.'})
        else:
            return JsonResponse({'status': 'failed', 'error': 'Card is not associated with any game.'})
    return JsonResponse({'status': 'failed'})


@csrf_exempt
def submit_association(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            game_id = data.get('game_id')
            card_id = data.get('card_id')
            association = data.get('association')

            print(f"Received data: game_id={game_id}, card_id={card_id}, association={association}")

            game = get_object_or_404(Game, id=game_id)
            card = get_object_or_404(Card, id=card_id)
            current_round = game.rounds.filter(active=True).first()

            # текущая карточка и ассоциацию
            current_round.current_card = card
            current_round.association = association
            current_round.save()

            # удаляем выбранную карточку у игрока
            player_card = PlayerCard.objects.get(player=game.current_player, card=card)
            player_card.in_hand = False
            player_card.save()

            # выбор карт ботами
            players = list(game.players.all())
            selected_cards = [player_card]
            for player in players:
                if player.is_bot:
                    bot_cards = PlayerCard.objects.filter(player=player, in_hand=True)
                    bot_choice = random.choice(bot_cards)
                    bot_choice.in_hand = False
                    bot_choice.save()
                    selected_cards.append(bot_choice)
            # перемешивание
            random.shuffle(selected_cards)
            # Переход хода к следующему
            current_player_index = players.index(game.current_player)
            next_player_index = (current_player_index + 1) % len(players)
            game.current_player = players[next_player_index]
            game.save()
            print("Association submitted successfully")
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error in submit_association: {e}")
            print(f"Error in submit_association: {e}")
            return JsonResponse({'status': 'failed', 'error': str(e)})
    return JsonResponse({'status': 'failed'})
