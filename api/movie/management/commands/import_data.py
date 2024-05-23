from django.core.management.base import BaseCommand
import pandas as pd
from movie.models import Movie, Genre
from datetime import datetime

class Command(BaseCommand):
    help = 'Import data from CSV file'

    def handle(self, *args, **kwargs):
        # Read the CSV file into a DataFrame
        file_path = r'C:\Users\lucas\Downloads\modified_file.csv'
        df = pd.read_csv(file_path)

        batch_size = 1000  # You can adjust the batch size based on your requirements
        movies_to_create = []
        genres_to_add = {}

        for index, row in df.iterrows():
            title = row['title']
            description = row['overview']

            try:
                release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                release_date = None  # Handle invalid or missing date

            poster_url = row['poster_path']

            movie = Movie(
                title=title,
                description=description,
                release_date=release_date,
                poster_url=poster_url
            )

            movies_to_create.append(movie)

            genres = row['genres']
            if isinstance(genres, str):
                genres = genres.split('-')
                for genre_name in genres:
                    genre_name = genre_name.strip()
                    if genre_name not in genres_to_add:
                        genres_to_add[genre_name] = []
                    genres_to_add[genre_name].append(movie)

            # Batch insert movies
            if len(movies_to_create) >= batch_size:
                self._bulk_create_movies(movies_to_create, genres_to_add)
                movies_to_create = []
                genres_to_add = {}

        # Insert any remaining movies
        if movies_to_create:
            self._bulk_create_movies(movies_to_create, genres_to_add)

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))

    def _bulk_create_movies(self, movies_to_create, genres_to_add):
        Movie.objects.bulk_create(movies_to_create)
        
        # After movies are created, handle genre associations
        for genre_name, movies in genres_to_add.items():
            genre, _ = Genre.objects.get_or_create(name=genre_name)
            for movie in movies:
                movie.genres.add(genre)
                movie.save()

        self.stdout.write(self.style.SUCCESS('Batch imported successfully'))
