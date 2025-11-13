from rest_framework import serializers
from .models import Game, Developer, Publisher, Genre, GameGenre

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
        fields = ['id', 'game', 'genre'] # 'id' - це PK для GameGenre

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