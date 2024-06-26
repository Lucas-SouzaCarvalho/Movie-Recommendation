from mlxtend.frequent_patterns import apriori, association_rules
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Count, Avg
from .models import Movie, WatchedList, Rating
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from movie.serializers import MovieSerializer
from collections import Counter

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # Get the user's watched list
            watched_list = WatchedList.objects.filter(user=request.user)
            watched_movies = [entry.movie for entry in watched_list]
            
            # Calculate the frequency of each genre in the watched list
            genre_counter = Counter()
            for movie in watched_movies:
                for genre in movie.genres.all():
                    genre_counter[genre] += 1
            
            # Get the user's favorite genres
            favorite_genres = request.user.favorite_genres.all()
            
            # Combine favorite genres and frequently watched genres, sorted by frequency
            combined_genres = sorted(favorite_genres, key=lambda g: genre_counter.get(g, 0), reverse=True)
            
            # Find movies belonging to the combined genres that the user hasn't watched
            recommended_movies = (
                Movie.objects
                .filter(genres__in=combined_genres)
                .exclude(watchedlist__user=request.user)
                .annotate(avg_rating=Avg('rating__rating'))
                .order_by('-avg_rating')[:20]  # Limit the queryset to the top 20 movies
            )

            # Serialize the recommended movies
            serializer = MovieSerializer(recommended_movies, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
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

class SimilarityRecommendationView(APIView):
    def get(self, request, movie_id):
        try:
            # Fetch the target movie
            target_movie = Movie.objects.get(id=movie_id)
            target_keywords = target_movie.keywords.split('-')

            # Collect all movies data (id, title, poster_url, keywords) except for the target movie
            all_movies = Movie.objects.exclude(id=movie_id)
            movie_data = []
            for movie in all_movies:
                keywords = movie.keywords.split('-')
                movie_data.append({
                    'id': movie.id,
                    'title': movie.title,
                    'poster_url': movie.poster_url,
                    'keywords': " ".join(keywords),
                })

            # Prepare TF-IDF vectors for each movie
            documents = [movie['keywords'] for movie in movie_data]
            tfidf_vectorizer = TfidfVectorizer(tokenizer=lambda text: text.split(), lowercase=False)
            tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
            target_document = " ".join(target_keywords)
            target_vector = tfidf_vectorizer.transform([target_document])

            # Calculate cosine similarity between the target movie and all other movies
            similarity_scores = cosine_similarity(target_vector, tfidf_matrix)

            # Sort movies by similarity score
            sorted_indices = similarity_scores.argsort(axis=1).flatten()[::-1]
            recommendations = []
            for index in sorted_indices:
                movie = movie_data[index]
                recommendations.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'poster_url': movie['poster_url'],
                    'similarity_score': similarity_scores[0, index],
                })

            return Response(recommendations[:10], status=status.HTTP_200_OK)
        except Movie.DoesNotExist:
            return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
