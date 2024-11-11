from rest_framework import serializers
from .models import Genre, Movie, WatchedList, Rating, FavoriteMovie
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail

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
                  'tagline', 'credit', 'keywords', 'backdrop_path', 'youtube_path']


class UserSerializer(serializers.ModelSerializer):
    favorite_genres = GenreSerializer(many=True, read_only=True)
    favorite_genres_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), source='favorite_genres', write_only=True, many=True
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'favorite_genres', 'favorite_genres_ids']

class FavoriteMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteMovie
        fields = ['movie', 'added_at']

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
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user is associated with this email address.")
        return value

    def save(self):
        request = self.context.get('request')
        user = User.objects.get(email=self.validated_data['email'])
        
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        reset_url = f"{request.build_absolute_uri('/reset-password/')}?uid={uid}&token={token}"
        
        # Send email
        send_mail(
            subject="Password Reset",
            message=f"Click the link to reset your password: {reset_url}",
            from_email="directorscut731@gmail.com",
            recipient_list=[user.email]
        )
