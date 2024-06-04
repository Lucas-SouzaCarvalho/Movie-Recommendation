from django.core.management.base import BaseCommand
from django.db import transaction
import pandas as pd
from movie.models import Movie, Genre
from datetime import datetime

class Command(BaseCommand):
    help = 'Import data from CSV file'

    def handle(self, *args, **kwargs):
        # Read the CSV file into a DataFrame
        file_path = r'C:\Users\lucas\Downloads\filtered_file.csv'
        df = pd.read_csv(file_path)

        batch_size = 5000  # You can adjust the batch size based on your requirements
        movies_to_create = []
        genres_to_add = {}

        try:
            with transaction.atomic():
                for index, row in df.iterrows():
                    title = row['title']
                    description = row['overview']

                    try:
                        release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        release_date = None  # Handle invalid or missing date

                    poster_url = row['poster_path']
                    original_language = row['original_language']
                    production_companies = row['production_companies']
                    
                    try:
                        runtime = int(row['runtime'])
                    
                    except (ValueError, TypeError):
                        runtime = 1

                    status = row['status']
                    tagline = row['tagline']
                    credit = row['credits']
                    keywords = row['keywords']
                    backdrop_path = row['backdrop_path']

                    movie = Movie(
                        title=title,
                        description=description,
                        release_date=release_date,
                        poster_url=poster_url,
                        original_language=original_language,
                        runtime=runtime,
                        status=status,
                        tagline=tagline,
                        backdrop_path=backdrop_path,
                        production_companies=production_companies,
                        credit = credit,
                        keywords = keywords
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

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
            # Rollback the transaction
            transaction.set_rollback(True)

    def _bulk_create_movies(self, movies_to_create, genres_to_add):
        # Bulk create movies
        created_movies = Movie.objects.bulk_create(movies_to_create)
        
        # Create genre associations in bulk
        movie_genre_relations = []
        for movie in created_movies:
            for genre_name, movies in genres_to_add.items():
                if movie in movies:
                    genre, _ = Genre.objects.get_or_create(name=genre_name)
                    movie_genre_relations.append(Movie.genres.through(movie_id=movie.id, genre_id=genre.id))

        # Bulk create movie-genre relations
        Movie.genres.through.objects.bulk_create(movie_genre_relations)

        self.stdout.write(self.style.SUCCESS('Batch imported successfully'))
