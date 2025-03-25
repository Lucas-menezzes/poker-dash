from django.contrib import admin
from django.urls import path
from results import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),

    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('start_game/', views.start_game, name='start_game'),
    path('games/', views.game_page, name='game_page'),
    path('add_player/', views.add_player, name='add_player'),
    path('end_game/', views.end_game, name='end_game'),
    path('add_buyin/', views.add_buyin, name='add_buyin'),
    path('finalize_debit/', views.finalize_debit, name='finalize_debit'),
    path('historic/', views.historic, name='historic'),

]
