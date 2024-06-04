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
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release_date', 'genres', 'poster_url',
                  'original_language', 'production_companies', 'runtime', 'status',
                  'tagline', 'credits', 'keywords', 'backdrop_path']


class UserSerializer(serializers.ModelSerializer):
    favorite_genres = GenreSerializer(many=True, read_only=True)
    favorite_genres_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), source='favorite_genres', write_only=True, many=True
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'favorite_genres', 'favorite_genres_ids']

class WatchedListSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True
    )

    class Meta:
        model = WatchedList
        fields = ['id', 'user', 'movie', 'movie_id', 'watched_date']
        read_only_fields = ['user', 'watched_date']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class RatingSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True
    )

    class Meta:
        model = Rating
        fields = ['id', 'user', 'movie', 'movie_id', 'rating']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
