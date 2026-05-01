from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken 
from .models import User
from rest_framework import viewsets, status, permissions
from .models import User, Tender, Field
from .serializers import UserSerializer, TenderSerializer, FieldSerializer
from .models import Tender, Field, Bid, SavedTender
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import TenderSerializer, FieldSerializer, BidSerializer, SavedTenderSerializer
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user: User = serializer.save()
            user.set_password(request.data['password'])
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            },
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                "User logged out successfully",
                status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(
                "User not logged in",
                status=status.HTTP_400_BAD_REQUEST)
            
class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description'] 
    filterset_fields = {
        'fields__name': ['exact', 'icontains'], 
    }    

class FieldViewSet(viewsets.ModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
class SavedTenderViewSet(viewsets.ModelViewSet):
    queryset = SavedTender.objects.all()
    serializer_class = SavedTenderSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
