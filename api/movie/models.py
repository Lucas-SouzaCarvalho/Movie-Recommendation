from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField(null = True)
    genres = models.ManyToManyField(Genre)  # Many-to-many relationship with Genre
    poster_url = models.URLField(max_length=200, null=True, blank=True)

class User(AbstractUser):
    favorite_genres = models.ManyToManyField(Genre, related_name='users', blank=True)
    groups = models.ManyToManyField(Group, related_name='auth_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='auth_user_permissions')

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