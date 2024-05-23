from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = 'Delete all movies from the database'

    def handle(self, *args, **kwargs):
        count, _ = Movie.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} movies'))