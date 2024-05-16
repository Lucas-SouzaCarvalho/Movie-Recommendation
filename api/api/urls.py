from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from movie.apriori import MovieRecommendationView
from movie.views import GenreViewSet, MovieViewSet, RatingViewSet, UserRegistrationView, UserViewSet, WatchedListViewSet, logout, CustomTokenObtainPairView, CustomTokenRefreshView
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
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
    path('recommendations/', MovieRecommendationView.as_view(), name='movie_recommendations'),
    path('users/<int:pk>/add-favorite-genre/', UserViewSet.as_view({'post': 'add_favorite_genre'}), name='add_favorite_genre'),
    path('users/<int:pk>/remove-favorite-genre/', UserViewSet.as_view({'post': 'remove_favorite_genre'}), name='remove_favorite_genre'),
    path('', include(router.urls)),
]