from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.main_menu, name='main_menu'),
    path('select_game/', views.select_game, name='select_game'),
    path('create_game/', views.create_game, name='create_game'),
    path('join_game/', views.join_game, name='join_game'),
    path('game_board/', views.game_board, name='game_board'),
    path('choose_card/<int:card_id>/', views.choose_card, name='choose_card'),
    path('submit_association/', views.submit_association, name='submit_association'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)