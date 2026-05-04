from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

# Create your views here.
class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


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
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
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
        

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name', 'email', 'company__company_name']
    filterset_fields = {
        'gender': ['exact'],
        'company__company_name': ['exact', 'icontains'],
        'company__location__city': ['exact', 'icontains'],
    }

class TenderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description'] 
    filterset_fields = {
        'category__name': ['exact', 'icontains'],
        'status__name': ['exact'],
        'location__city': ['exact', 'icontains'],
        'location__state': ['exact', 'icontains'],
        'location__street': ['exact', 'icontains'],
        'user__company__company_name': ['exact', 'icontains'],
    }    

class BidViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'proposal']
    filterset_fields = {
        'tender__title': ['exact', 'icontains'],
        'tender__description': ['exact', 'icontains'],
        'tender__category__name': ['exact', 'icontains'],
        'tender__status': ['exact'],
        'tender__location__city': ['exact', 'icontains'],
        'tender__location__state': ['exact', 'icontains'],
        'tender__location__street': ['exact', 'icontains'],
        'tender__user__company__company_name': ['exact', 'icontains'],
        'total_price': ['exact', 'lt', 'gt'],
    }

#Read-only viewsets for categories, statuses, currencies, and locations
#used to populate dropdowns in the frontend and should not be modified by users
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']