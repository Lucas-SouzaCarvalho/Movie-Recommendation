import pandas as pd
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Drop specified columns from the CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--file_path', type=str, help='Path to the CSV file', required=True)
        

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        # Load the CSV file
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('File not found'))
            return

        # Filter the DataFrame to keep only rows with a poster_path
        df_filtered = df[df['poster_path'].notna()]

        # Save the filtered DataFrame to a new CSV file (optional)
        df_filtered.to_csv("filtered_file.csv", index=False)

        # Print a message to confirm the deletion
        print("Rows without poster_path have been deleted.")

