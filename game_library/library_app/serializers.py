from rest_framework import serializers
from .models import User, Order, Library, LibraryGame, OrderGame, Game, Developer, Publisher, Genre, GameGenre

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email','date_joined','password']
        read_only_fields = ['date_joined']

class OrderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)

    class Meta:
        model = Order
        fields = ['order_id','user','username','total_amount','status','created_at']
        read_only_fields = ['created_at']

class LibrarySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)

    class Meta:
        model = Library
        fields = ['library_id','user','username']

class LibraryGameSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source='game.title',read_only=True)
    library_user = serializers.CharField(source='library.user.username',read_only=True)

    class Meta:
        model = LibraryGame
        fields = ['id','library','game','game_title','library_user','playtime_hours','purchase_date','is_installed','last_played']
        read_only_fields = ['purchase_date','last_played']

class OrderGameSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source='game.title',read_only=True)

    class Meta:
        model = OrderGame
        fields = ['id','order','game','game_title','price_at_purchase']
        read_only_fields = ['price_at_purchase']

class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = ['developer_id', 'name', 'description']

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['publisher_id', 'name', 'description']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['genre_id', 'name']

class GameGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameGenre
        fields = ['id', 'game', 'genre'] 

class GameSerializer(serializers.ModelSerializer):
    developer = serializers.StringRelatedField()
    publisher = serializers.StringRelatedField()
    genre = serializers.StringRelatedField(many=True)

    class Meta:
        model = Game
        fields = [
            'game_id', 'title', 'description', 'price',
            'release_date', 'developer', 'publisher', 'genre'
        ]


class GameWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = [
            'title', 'description', 'price', 'release_date',
            'developer', 'publisher', 'genre'
        ]

