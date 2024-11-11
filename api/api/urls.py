from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from movie.views import (
    GenreViewSet, MovieViewSet, RatingViewSet, UserRegistrationView, 
    UserViewSet, WatchedListViewSet, logout, CustomTokenObtainPairView, 
    CustomTokenRefreshView, MovieDetailView, AddToWatchedListView, 
    RemoveFromWatchedListView, AverageRatingView, PasswordResetView,
    FavoriteMovieViewSet
)
from movie.apriori import AprioriRecommendationView, GenreRecommendationView, RatingRecommendationView, SimilarityRecommendationView

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'genres', GenreViewSet)
router.register(r'movies', MovieViewSet)
router.register(r'watched-list', WatchedListViewSet)
router.register(r'favorites', FavoriteMovieViewSet, basename='favorite-movie')
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('average-ratings/', AverageRatingView.as_view(), name='average-ratings'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', logout, name='logout'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('movies/<int:pk>/', MovieDetailView.as_view(), name='movie-detail'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('recommendations/apriori/', AprioriRecommendationView.as_view(), name='apriori_recommendations'),
    path('recommendations/genre/', GenreRecommendationView.as_view(), name='genre_recommendations'),
    path('recommendations/rating/', RatingRecommendationView.as_view(), name='rating_recommendations'),
    path('recommendations/similarity/<int:movie_id>/', SimilarityRecommendationView.as_view(), name='similarity_recommendations'),
    path('users/<int:pk>/add-favorite-genre/', UserViewSet.as_view({'post': 'add_favorite_genre'}), name='add_favorite_genre'),
    path('users/<int:pk>/remove-favorite-genre/', UserViewSet.as_view({'post': 'remove_favorite_genre'}), name='remove_favorite_genre'),
    path('users/<int:pk>/change-username/', UserViewSet.as_view({'post': 'change_username'}), name='change_username'),
    path('movies/<int:movie_id>/rate/', RatingViewSet.as_view({'post': 'rate_movie'}), name='rate-movie'),
    path('movies/<int:movie_id>/user-rating/', RatingViewSet.as_view({'get': 'user_rating'}), name='user-movie-rating'),
    path('watched-list/add/', AddToWatchedListView.as_view(), name='add-to-watched-list'),
    path('watched-list/remove/', RemoveFromWatchedListView.as_view(), name='remove-from-watched-list'),
    path('', include(router.urls)),  # Includes all routes registered with the router
]
