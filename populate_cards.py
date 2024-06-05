import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imaginarium.settings')
django.setup()

from game.models import Card

cards_dir = os.path.join(settings.MEDIA_ROOT, 'cards')

cards_files = os.listdir(cards_dir)

# добавляем карточки в базу данных
for file_name in cards_files:
    card_description = os.path.splitext(file_name)[0]
    card_image_path = os.path.join('cards', file_name)
    card, created = Card.objects.get_or_create(description=card_description, defaults={'image': card_image_path})
    if created:
        print(f'Card created: {card_description}')
    else:
        print(f'Card already exists: {card_description}')
