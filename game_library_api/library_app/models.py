from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00, message='Баланс не може бути від’ємним.')]
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'

class Developer(models.Model):
    developer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'developer'

class Publisher(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'publisher'

class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'genre'

class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    release_date = models.DateField()
    developer = models.ForeignKey(Developer, on_delete=models.SET_NULL, null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True)
    genre = models.ManyToManyField(Genre, through='GameGenre')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'game'

class Library(models.Model):
    library_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    games = models.ManyToManyField(Game, through='LibraryGame')

    def __str__(self):
        return f"{self.user.username}'s library"

    class Meta:
        db_table = 'library'

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [('pending','Pending'),
                      ('complete','Complete'),
                      ('canceled','Canceled')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(decimal_places=2, max_digits=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    games = models.ManyToManyField(Game, through='OrderGame')

    def __str__(self):
        return f"Order #{self.order_id} by {self.user.username}"

    class Meta:
        db_table = 'order'


class GameGenre(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.game.title} - {self.genre.name}"

    class Meta:
        db_table = 'game_genre'
        unique_together = ('game', 'genre')

class LibraryGame(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    playtime_hours = models.PositiveIntegerField(default=0)
    purchase_date = models.DateField(null=True, blank=True)
    last_played = models.DateTimeField(null=True, blank=True)
    is_installed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.library.user.username} - {self.game.title}"

    class Meta:
        db_table = 'library_game'
        unique_together = ('library', 'game')

class OrderGame(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price_at_purchase = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"Order #{self.order.order_id} - {self.game.title}"

    class Meta:
        db_table = 'order_game'
        unique_together = ('order', 'game')





