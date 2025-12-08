from rest_framework import serializers
from .models import User, Order, Library, LibraryGame, OrderGame, Game, Developer, Publisher, Genre, GameGenre, Review


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email','date_joined','password','balance']
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

class OrderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)

    class Meta:
        model = Order
        fields = ['order_id','user','username','total_amount','status','created_at']
        read_only_fields = ['created_at']


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
    developer_name = serializers.StringRelatedField(source='developer', read_only=True)
    publisher_name = serializers.StringRelatedField(source='publisher', read_only=True)
    genre_names = serializers.StringRelatedField(source='genre', many=True, read_only=True)

    developer_id = serializers.PrimaryKeyRelatedField(
        source='developer',
        queryset=Developer.objects.all(),
        required=False,
        allow_null=True
    )

    publisher_id = serializers.PrimaryKeyRelatedField(
        source='publisher',
        queryset=Publisher.objects.all(),
        required=False,
        allow_null=True
    )

    genre_id = serializers.PrimaryKeyRelatedField(
        source='genre',
        many=True,
        queryset=Genre.objects.all()
    )

    is_owned = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            'game_id', 'title', 'description', 'price',
            'release_date',
            'developer_name', 'publisher_name', 'genre_names',
            'developer_id', 'publisher_id', 'genre_id',
            'is_owned'
        ]

    def get_is_owned(self, obj):
        user_owned_game_ids = self.context.get('user_owned_game_ids', set())
        return obj.game_id in user_owned_game_ids


class LibraryGameSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source='game.title',read_only=True)
    library_user = serializers.CharField(source='library.user.username',read_only=True)
    game_data = GameSerializer(source='game', read_only=True)

    class Meta:
        model = LibraryGame
        fields = ['id','library','game','game_title','library_user','playtime_hours','purchase_date','is_installed','last_played', 'game_data'] # ⬅️ ДОДАНО game_data
        read_only_fields = ['purchase_date','last_played']

class LibrarySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    library_games = LibraryGameSerializer(many=True, source='librarygame_set', read_only=True)

    class Meta:
        model = Library
        fields = ['library_id', 'user', 'username', 'library_games']

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    game_title = serializers.CharField(source='game.title', read_only=True)

    class Meta:
        model = Review
        fields = [
            'review_id', 'user', 'username',
            'game', 'game_title', 'rating',
            'comment', 'created_at'
        ]
        read_only_fields = ['created_at']

class PriceQualityReportSerializer(serializers.Serializer):
    title = serializers.CharField(source='game__title')
    price = serializers.DecimalField(source='game__price',max_digits=10,decimal_places=2)
    avg_rating = serializers.FloatField()
    reviews_count = serializers.IntegerField()
    ratio = serializers.FloatField(source='price_quality_ratio')

class GenrePlaytimeReportSerializer(serializers.Serializer):
    name = serializers.CharField()
    total_playtime = serializers.IntegerField()
    game_count = serializers.IntegerField()

class MonthlyRevenueReportSerializer(serializers.Serializer):
    order_year = serializers.IntegerField()
    order_month = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10,decimal_places=2)