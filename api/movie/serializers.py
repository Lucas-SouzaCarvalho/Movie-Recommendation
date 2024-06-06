from rest_framework import serializers
from .models import Genre, Movie, WatchedList, Rating
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

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
                  'tagline', 'credit', 'keywords', 'backdrop_path']


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

class AddWatchedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchedList
        fields = ['movie']

    def create(self, validated_data):
        user = self.context['request'].user
        movie = validated_data.get('movie')
        watched_movie, created = WatchedList.objects.get_or_create(user=user, movie=movie)
        return watched_movie

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

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])

        user_id = refresh.payload.get('user_id')
        user = User.objects.get(id=user_id)
        
        data['username'] = user.username
        data['id'] = user.id

        return data
