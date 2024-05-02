from rest_framework import serializers
from .models import Genre, Movie, WatchedList, Rating
from django.contrib.auth import get_user_model

User = get_user_model()  # Get the custom user model

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class MovieSerializer(serializers.ModelSerializer):
    genre = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all())

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release_date', 'genre', 'director', 'poster_url']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'favorite_genres']

class WatchedListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Assuming user is a ForeignKey

    class Meta:
        model = WatchedList
        fields = ['id', 'user', 'movie', 'watched_date']

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Assuming user is a ForeignKey

    class Meta:
        model = Rating
        fields = ['id', 'user', 'movie', 'rating']
