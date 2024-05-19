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

        # Iterate through DataFrame rows and import data
        for index, row in df.iterrows():
            # Extract data from the row
            
            title = row['title']
            description = row['overview']
            
            try:
                release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date()
            
            except (ValueError, TypeError):
                release_date = None  # Handle invalid or missing date
            
            poster_url = row['poster_path']

            # Create a Movie instance and populate it with the extracted data
            movie = Movie.objects.create(
                title=title,
                description=description,
                release_date=release_date,
                poster_url=poster_url
            )

            # Extract genre data and create Genre instances if necessary
            genres = row['genres']
            if isinstance(genres, str):
                genres = genres.split('-')
                for genre_name in genres:
                    genre, _ = Genre.objects.get_or_create(name=genre_name.strip())
                    movie.genres.add(genre)

            # Save the Movie instance to the database
            movie.save()


        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
