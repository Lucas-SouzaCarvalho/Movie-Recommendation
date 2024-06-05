from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from movie.views import (
    GenreViewSet, MovieViewSet, RatingViewSet, UserRegistrationView, 
    UserViewSet, WatchedListViewSet, logout, CustomTokenObtainPairView, 
    CustomTokenRefreshView, MovieDetailView, AddToWatchedListView, RemoveFromWatchedListView
)
from movie.apriori import AprioriRecommendationView, GenreRecommendationView, RatingRecommendationView, SimilarityRecommendationView

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'genres', GenreViewSet)
router.register(r'movies', MovieViewSet)
router.register(r'watched-list', WatchedListViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', logout, name='logout'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('movies/<int:pk>/', MovieDetailView.as_view(), name='movie-detail'),
    path('recommendations/apriori/', AprioriRecommendationView.as_view(), name='apriori_recommendations'),
    path('recommendations/genre/', GenreRecommendationView.as_view(), name='genre_recommendations'),
    path('recommendations/rating/', RatingRecommendationView.as_view(), name='rating_recommendations'),
    path('recommendations/similarity/<int:movie_id>/', SimilarityRecommendationView.as_view(), name='similarity_recommendations'),
    path('users/<int:pk>/add-favorite-genre/', UserViewSet.as_view({'post': 'add_favorite_genre'}), name='add_favorite_genre'),
    path('users/<int:pk>/remove-favorite-genre/', UserViewSet.as_view({'post': 'remove_favorite_genre'}), name='remove_favorite_genre'),
    path('watched-list/add/', AddToWatchedListView.as_view(), name='add-to-watched-list'),
    path('watched-list/remove/', RemoveFromWatchedListView.as_view(), name='remove-from-watched-list'),
    path('', include(router.urls)),  # Includes all routes registered with the router
]
