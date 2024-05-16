from rest_framework import viewsets, permissions, status, filters, generics
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from .models import Genre, Movie, WatchedList, Rating
from .serializers import GenreSerializer, MovieSerializer, UserRegistrationSerializer, UserSerializer, WatchedListSerializer, RatingSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model  # Import get_user_model function

User = get_user_model()  # Get the custom user model

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    try:
        refresh_token = request.data['refresh']
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"success": "User logged out successfully."}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]  # Add JWT authentication
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_favorite_genre(self, request, pk=None):
        user = self.get_object()
        genre_ids = request.data.get('genre_ids', [])  # Accepts a list of genre_ids
        added_genres = []

        for genre_id in genre_ids:
            try:
                genre = Genre.objects.get(pk=genre_id)
                user.favorite_genres.add(genre)
                added_genres.append(genre.name)
            except Genre.DoesNotExist:
                pass  # Handle the case where the genre ID is invalid

        user.save()
        
        if added_genres:
            return Response({'status': f'Genres {", ".join(added_genres)} added to favorites'})
        else:
            return Response({'error': 'No valid genre IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
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
                pass  # Handle the case where the genre ID is invalid

        user.save()

        if removed_genres:
            return Response({'status': f'Genres {", ".join(removed_genres)} removed from favorites'})
        else:
            return Response({'error': 'No valid genre IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    authentication_classes = [JWTAuthentication]  # Add JWT authentication
    permission_classes = [permissions.IsAuthenticated]

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['title', 'release_date', 'director']
    search_fields = ['title', 'description', 'director']

    def get_queryset(self):
        queryset = Movie.objects.all()
        genre = self.request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genre__name=genre)
        # Add more filters as needed (e.g., release date range)

        return queryset

class WatchedListViewSet(viewsets.ModelViewSet):
    queryset = WatchedList.objects.all()
    serializer_class = WatchedListSerializer
    authentication_classes = [JWTAuthentication]  # Add JWT authentication
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, str):  # If user is a string (username), convert it to User instance
            try:
                user = User.objects.get(username=user)
            except User.DoesNotExist:
                return WatchedList.objects.none()  # Return empty queryset if user does not exist
        return WatchedList.objects.filter(user=user)

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    authentication_classes = [JWTAuthentication]  # Add JWT authentication
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, str):  # If user is a string (username), convert it to User instance
            try:
                user = User.objects.get(username=user)
            except User.DoesNotExist:
                return Rating.objects.none()  # Return empty queryset if user does not exist
        return Rating.objects.filter(user=user)

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Corrected permission class to use the UserRegistrationSerializer

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