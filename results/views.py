import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Player, Game, GamePlayer, Purchase, Transaction
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

@csrf_exempt
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        name = request.POST['name']

        player = Player.objects.create_user(username=username, password=password, name=name)
        login(request, player)
        return redirect('/')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_exempt
@login_required 
def start_game(request):
    try:
        Game.objects.filter(active=True).update(active=False)
        game = Game.objects.create(active=True)

        print(f"Jogo criado com ID: {game.id}, ativo: {game.active}")

        return JsonResponse({'success': True, 'message': 'Jogo iniciado com sucesso!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao iniciar o jogo: {str(e)}'})

def game_page(request):
    players = Player.objects.all()

    if request.method == "POST":
        selected_players = request.POST.getlist('players') 
        if selected_players:
            game = Game.objects.create() 
            for player_id in selected_players:
                player = Player.objects.get(id=player_id)
                game.players.add(player)
            game.save()
            messages.success(request, "Jogo iniciado com sucesso!")
            return redirect('game_page')
        else:
            messages.error(request, "Por favor, selecione pelo menos um jogador.")

    games = Game.objects.all().order_by('-start_time')
    return render(request, 'game_page.html', {'players': players, 'games': games})

def dashboard(request):
    players = Player.objects.all()
    total_balance = sum(player.balance for player in players)
    return render(request, 'dashboard.html', {'players': players, 'total_balance': total_balance})



@csrf_exempt
def add_player(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player_id = data.get('player_id')

            if not player_id:
                return JsonResponse({'success': False, 'message': 'ID do jogador não fornecido.'})

            player = Player.objects.get(id=player_id)

            try:
                game = Game.objects.filter(active=True).latest('start_time')
                print(f"Jogo ativo encontrado com ID: {game.id}, ativo: {game.active}")
            except Game.DoesNotExist:
                print("Nenhum jogo ativo encontrado.")
                return JsonResponse({'success': False, 'message': 'Nenhum jogo ativo encontrado.'})

            
            player.attendance += 1
            player.save()
            game_player, created = GamePlayer.objects.get_or_create(game=game, player=player)

            return JsonResponse({
                'success': True,
                'player': {
                    'id': player.id,
                    'name': player.name,
                    'purchases': game_player.total_purchases,
                    'credits': float(game_player.total_credits)
                }
            })
        except Player.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Jogador não encontrado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro inesperado: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Requisição inválida.'})

@csrf_exempt
def add_buyin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        player_id = data.get('player_id')
        amount = data.get('BUY_IN_VALUE', 40.00)

        try:
            player = Player.objects.get(id=player_id)
            game = Game.objects.filter(active=True).latest('start_time')
            game_player = GamePlayer.objects.get(game=game, player=player)

            game_player.total_purchases += 1
            game_player.total_credits += amount
            game_player.save()
            
            player.purchases += 1
            player.credits += Decimal(amount)
            player.save()

            Purchase.objects.create(game_player=game_player, amount=amount)

            return JsonResponse({
                'success': True,
                'credits': game_player.total_credits,
                'purchases': game_player.total_purchases
            })
        except Player.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Jogador não encontrado.'})
    return JsonResponse({'success': False, 'message': 'Requisição inválida.'})

@csrf_exempt
def end_game(request):
    if request.method == 'POST':
        try:
            game = Game.objects.filter(active=True).latest('start_time')

            game_players = GamePlayer.objects.filter(game=game)
            if not game_players.exists():
                return JsonResponse({'success': False, 'message': 'Não há jogadores registrados neste jogo.'})

            game.active = False
            game.end_time = datetime.now()
            game.save()

            game_players = GamePlayer.objects.filter(game=game)
            players_data = []
            for gp in game_players:
                players_data.append({
                    'id': gp.player.id,
                    'name': gp.player.name,
                    'total_purchases': gp.total_purchases,
                    'total_credits': float(gp.total_credits)
                })

            return JsonResponse({
                'success': True,
                'game_id': game.id,
                'start_time': game.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': game.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'players': players_data
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Requisição inválida.'})

@csrf_exempt
def finalize_debit(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player_id = data.get('player_id')
            devolver = Decimal(data.get('devolver', 0))

            player = Player.objects.get(id=player_id)
            player.debits += devolver
            player.save()

            print(f"Débito registrado para o jogador {player.name}: R$ {devolver}")
            return JsonResponse({'success': True})
        except Player.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Jogador não encontrado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro inesperado: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Requisição inválida.'})

@csrf_exempt
def historic(request):
    games = Game.objects.all().order_by('-start_time')
    game_data = []
    if not games.exists():
            print("Nenhum jogo encontrado no banco de dados.")
    for game in games:
        game_players = GamePlayer.objects.filter(game=game)
        total_compras = sum(gp.total_credits for gp in game_players)
        game_data.append({
            'game': game,
            'total_compras': total_compras
        })

    return render(request, 'historic.html', {'game_data': game_data})