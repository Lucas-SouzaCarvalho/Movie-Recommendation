from django.core.management.base import BaseCommand
from django.db import models
from movie.models import Movie, Genre

class Command(BaseCommand):
    help = 'Delete all movies from the database and clean up genres with no associated movies'

    def handle(self, *args, **kwargs):
        # Delete all movies and capture the count
        movie_count, _ = Movie.objects.all().delete()
        
        # Find and delete genres that have no associated movies
        genres_to_delete = Genre.objects.annotate(num_movies=models.Count('movies')).filter(num_movies=0)
        genre_count = genres_to_delete.count()
        genres_to_delete.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {movie_count} movies'))
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {genre_count} genres with no associated movies'))
