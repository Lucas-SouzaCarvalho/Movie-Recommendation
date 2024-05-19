from mlxtend.frequent_patterns import apriori, association_rules
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from .models import Movie, WatchedList, Rating
import pandas as pd 

class AprioriRecommendationView(APIView):
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
            apriori_recommendations = {}
            for idx, row in rules.iterrows():
                if len(row['antecedents']) == 1:
                    movie_id = row['antecedents'].pop()
                    consequent = row['consequents'].pop()
                    support = row['support']
                    confidence = row['confidence']
                    if movie_id not in apriori_recommendations:
                        apriori_recommendations[movie_id] = []
                    apriori_recommendations[movie_id].append({'movie_id': consequent, 'support': support, 'confidence': confidence})

            return Response(apriori_recommendations, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenreRecommendationView(APIView):
    def get(self, request):
        try:
            # Get the user's favorite genres
            favorite_genres = request.user.favorite_genres.all()

            # Find movies belonging to the user's favorite genres that the user hasn't watched
            recommended_movies = Movie.objects.filter(genres__in=favorite_genres).exclude(watched__user=request.user)

            return Response(recommended_movies.values('id', 'title', 'description', 'release_date', 'poster_url'), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RatingRecommendationView(APIView):
    def get(self, request):
        try:
            highest_rated_movies = Rating.objects.values('movie').annotate(avg_rating=Avg('rating')).order_by('-avg_rating')[:10]

            # Exclude movies the user has already watched
            recommended_movies = Movie.objects.exclude(rating__user=request.user, id__in=[movie['movie'] for movie in highest_rated_movies])

            return Response(recommended_movies.values('id', 'title', 'description', 'release_date', 'poster_url'), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
