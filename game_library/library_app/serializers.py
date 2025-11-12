from rest_framework import serializers
from library_app.models import User, Order, Library, LibraryGame, OrderGame

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
        read_only_fields = ['created_at','total_amount']

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
