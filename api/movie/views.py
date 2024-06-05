from rest_framework import viewsets, permissions, status, filters, generics
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Avg, Q
from .models import Genre, Movie, WatchedList, Rating
from .serializers import (
    GenreSerializer, MovieSerializer, UserRegistrationSerializer, 
    UserSerializer, WatchedListSerializer, RatingSerializer, AddWatchedListSerializer
)

User = get_user_model()

class MovieDetailView(APIView):
    def get(self, request, pk):
        try:
            movie = Movie.objects.get(pk=pk)
        except Movie.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.outstanding_token = None  # Invalidate the refresh token
            return Response({"success": "User logged out successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Refresh token not provided"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return a queryset containing only the current user
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        # Return the current user instance
        return self.request.user

    @action(detail=True, methods=['post'], url_path='add-favorite-genre')
    def add_favorite_genre(self, request, pk=None):
        user = self.get_object()
        genre_ids = request.data.get('genre_ids', [])
        added_genres = []

        for genre_id in genre_ids:
            try:
                genre = Genre.objects.get(pk=genre_id)
                user.favorite_genres.add(genre)
                added_genres.append(genre.name)
            except Genre.DoesNotExist:
                continue

        user.save()

        if added_genres:
            return Response({'status': f'Genres {", ".join(added_genres)} added to favorites'})
        else:
            return Response({'error': 'No valid genre IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='remove-favorite-genre')
    def remove_favorite_genre(self, request, pk=None):
        user = self.get_object()
        genre_ids = request.data.get('genre_ids', [])
        removed_genres = []

        for genre_id in genre_ids:
            try:
                genre = Genre.objects.get(pk=genre_id)
                user.favorite_genres.remove(genre)
                removed_genres.append(genre.name)
            except Genre.DoesNotExist:
                continue

        user.save()

        if removed_genres:
            return Response({'status': f'Genres {", ".join(removed_genres)} removed from favorites'})
        else:
            return Response({'error': 'No valid genre IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['title', 'release_date']
    search_fields = ['title', 'description', 'production_companies', 'credit', 'genres__name']
    pagination_class = StandardResultsSetPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        genre = self.request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genres__name__iexact=genre.strip())
        
        production_companies = self.request.query_params.get('production_companies')
        if production_companies:
            company_names = production_companies.split('-')
            queries = [Q(production_companies__icontains=company.strip()) for company in company_names]
            query = queries.pop()
            for item in queries:
                query |= item
            queryset = queryset.filter(query)
        
        credit = self.request.query_params.get('credit')
        if credit:
            credit_names = credit.split('-')
            queries = [Q(credit__icontains=name.strip()) for name in credit_names]
            query = queries.pop()
            for item in queries:
                query |= item
            queryset = queryset.filter(query)

        search = self.request.query_params.get('search')
        if search:
            search_queries = [
                Q(title__icontains=search),
                Q(description__icontains=search),
                Q(production_companies__icontains=search),
                Q(credit__icontains=search),
                Q(genres__name__icontains=search),
            ]
            search_query = search_queries.pop()
            for item in search_queries:
                search_query |= item
            queryset = queryset.filter(search_query)

        return queryset.distinct()

class WatchedListViewSet(viewsets.ModelViewSet):
    queryset = WatchedList.objects.all()
    serializer_class = WatchedListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return WatchedList.objects.filter(user=user)
    
class AddToWatchedListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddWatchedListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Movie added to watched list successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromWatchedListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        movie_id = request.data.get('movie_id')
        if not movie_id:
            return Response({"error": "movie_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        try:
            watched_list_entry = WatchedList.objects.get(user=user, movie_id=movie_id)
            watched_list_entry.delete()
            return Response({"message": "Movie removed from watched list successfully."}, status=status.HTTP_200_OK)
        except WatchedList.DoesNotExist:
            return Response({"error": "Movie not found in your watched list"}, status=status.HTTP_404_NOT_FOUND)

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Rating.objects.filter(user=user)
    
    @action(detail=False, methods=['get'], url_path='average-ratings')
    def average_ratings(self, request):
        average_ratings = Rating.objects.values('movie').annotate(avg_rating=Avg('rating')).order_by('-avg_rating')
        return Response(average_ratings, status=status.HTTP_200_OK)

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        response.data['username'] = user.username
        return response

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        response.data['username'] = user.username
        return response
