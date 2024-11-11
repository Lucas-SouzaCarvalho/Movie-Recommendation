from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group


# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField(null=True)
    genres = models.ManyToManyField(Genre)
    poster_url = models.URLField(max_length=200, null=True, blank=True)
    original_language = models.CharField(max_length=50, null=True, blank=True)
    production_companies = models.TextField(null=True, blank=True)
    runtime = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    tagline = models.CharField(max_length=255, null=True, blank=True)
    credit = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True)
    backdrop_path = models.URLField(max_length=200, null=True, blank=True)
    youtube_path = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.title

class User(AbstractUser):
    favorite_genres = models.ManyToManyField(Genre, related_name='users', blank=True)
    groups = models.ManyToManyField(Group, related_name='auth_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='auth_user_permissions')

class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'movie'], name='unique_user_movie')
        ]

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

class WatchedList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watched')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched_date = models.DateField(auto_now_add=True)

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    RATINGS_CHOICES = [
        (0.5, '0.5 star'),
        (1.0, '1 star'),
        (1.5, '1.5 stars'),
        (2.0, '2 stars'),
        (2.5, '2.5 stars'),
        (3.0, '3 stars'),
        (3.5, '3.5 stars'),
        (4.0, '4 stars'),
        (4.5, '4.5 stars'),
        (5.0, '5 stars'),
    ]
    rating = models.FloatField(choices=RATINGS_CHOICES, null=True)