from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets, filters

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from .serializers import *
from .models import *


class EmailTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = EmailTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):

    def post(self, request):

        try:

            refresh_token = request.data["refresh"]

            token = RefreshToken(refresh_token)

            token.blacklist()

            return Response(
                "User logged out successfully",
                status=status.HTTP_205_RESET_CONTENT
            )

        except Exception:

            return Response(
                "User not logged in",
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()

    serializer_class = UserSerializer

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend
    ]

    search_fields = [
        'first_name',
        'last_name',
        'email'
    ]


class TenderViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]

    queryset = Tender.objects.filter(
        is_approved=True
    )

    serializer_class = TenderSerializer

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend
    ]

    search_fields = [
        'title',
        'description'
    ]

    filterset_fields = {
        'category__name': ['exact', 'icontains'],
        'location__city': ['exact', 'icontains'],
        'location__state': ['exact', 'icontains'],
    }


class BidViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]

    queryset = Bid.objects.all()

    serializer_class = BidSerializer

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend
    ]

    search_fields = [
        'title',
        'proposal'
    ]


class SavedTenderViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]

    queryset = SavedTender.objects.all()

    serializer_class = SavedTenderSerializer


class EvaluationViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]

    queryset = Evaluation.objects.all()

    serializer_class = EvaluationSerializer


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