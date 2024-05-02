from mlxtend.frequent_patterns import apriori, association_rules
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import WatchedList
from .serializers import WatchedListSerializer
import pandas as pd

class MovieRecommendationView(APIView):
    def get(self, request):
        try:
            # Retrieve watched movies data for all users
            watched_movies_data = WatchedList.objects.all().values_list('user_id', 'movie_id')

            # Create a dictionary to track watched movies for each user
            user_watched_movies = {}
            for user_id, movie_id in watched_movies_data:
                if user_id not in user_watched_movies:
                    user_watched_movies[user_id] = set()
                user_watched_movies[user_id].add(movie_id)

            # Prepare the data for Apriori algorithm
            transactions = [{f'Movie_{movie_id}'} for movie_id in user_watched_movies]

            # Convert the data to a DataFrame
            df = pd.DataFrame(transactions)

            # Run the Apriori algorithm
            frequent_itemsets = apriori(df, min_support=0.1, use_colnames=True)

            # Generate recommendations
            rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
            recommendations = {}
            for idx, row in rules.iterrows():
                if len(row['antecedents']) == 1:
                    movie_id = row['antecedents'].pop()
                    consequent = row['consequents'].pop()
                    support = row['support']
                    confidence = row['confidence']
                    if movie_id not in recommendations:
                        recommendations[movie_id] = []
                    recommendations[movie_id].append({'movie_id': consequent, 'support': support, 'confidence': confidence})

            return Response(recommendations, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
