from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class PlayerManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("O usuário deve ter um nome de usuário")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class Player(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    purchases = models.PositiveIntegerField(default=0)
    credits = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    debits = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    attendance = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = PlayerManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.name} ({self.username}) - Saldo: {self.balance}"

    @property
    def balance(self):
        return self.debits - self.credits

    @property
    def value_per_day(self):
        if self.attendance > 0:
            return self.credits / self.attendance
        return 0.0

    @property
    def frequency(self):
        total_games = Game.objects.count()
        if total_games == 0:
            return 0.0
        frequencia = (self.attendance / total_games) * 100
        return min(frequencia, 100.0)

    def update_attendance(self):
        self.attendance += 1
        self.save()

    @property
    def is_staff(self):
        return self.is_admin

class Transaction(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of {self.amount} for {self.player.name} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"



class Game(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Game started on {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"


class GamePlayer(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    total_purchases = models.PositiveIntegerField(default=0)
    total_credits = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Player {self.player.name} in {self.game}"


class Purchase(models.Model):
    game_player = models.ForeignKey(GamePlayer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=40.00)  # Valor fixo do buy-in
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase of {self.amount} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"