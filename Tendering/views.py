from rest_framework.permissions import BasePermission, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
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
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend
    ]

    search_fields = [
        'first_name',
        'last_name',
        'email'
    ]

class IsVerifiedUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_verified)
class TenderViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, IsVerifiedUser]

    queryset = Tender.objects.all()

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
    def perform_create(self, serializer):
        bid = serializer.save(user=self.request.user)

        Notification.objects.create(
            recipient=bid.tender.user,
            sender=self.request.user,
            notification_type="new_bid",
            message=f'New bid submitted for "{bid.tender.title}"',

            tender_title=bid.tender.title,
            bid_title=bid.title
        )
        


class SavedTenderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SavedTender.objects.all()
    serializer_class = SavedTenderSerializer

    def destroy(self, request, *args, **kwargs):
        tender_id = kwargs.get('pk')
        try:
            # Look up the record by the logged-in user and the tender's ID
            instance = SavedTender.objects.get(user=request.user, tender_id=tender_id)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SavedTender.DoesNotExist:
            return Response(
                {"error": "Saved tender record not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )



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


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
class TenderAttachmentViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]

    queryset = TenderAttachment.objects.all()

    serializer_class = TenderAttachmentSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )

class CheckPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get("password")

        if request.user.check_password(password):
            return Response(
                {"valid": True, "message": "Password is correct"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"valid": False, "message": "Password is incorrect"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
class AcceptBidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, bid_id):

        try:
            bid = Bid.objects.get(id=bid_id)

        except Bid.DoesNotExist:
            return Response(
                {"error": "Bid not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # check if current user owns the tender
        if bid.tender.user != request.user:
            return Response(
                {"error": "You do not own this tender"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if Bid.objects.filter(tender=bid.tender, status__name="Awarded").exists():
            return Response({"error": "Tender already finalized"})
        
        if bid.status.name == "Rejected":
            return Response({"error": "Cannot accept a rejected bid"})

        if bid.status.name == "Awarded":
            return Response({"error": "Bid already accepted"})

        accepted_status = Status.objects.get(name="Awarded")

        bid.status = accepted_status
        bid.save()
        other_bids = Bid.objects.filter(
            tender=bid.tender
        ).exclude(id=bid.id)

        other_bids.update(status=Status.objects.get(name="Rejected"))
        
        Notification.objects.create(
            recipient=bid.user,
            sender=request.user,
            notification_type="bid_accepted",
            message=f'Your bid for "{bid.tender.title}" was accepted.',
            tender_title=bid.tender.title,
            bid_title=bid.title
        )
      
        
        
       
        notifications = [
            Notification(
                recipient=b.user,
                sender=request.user,
                notification_type="bid_rejected",
                message=f'Your bid for "{bid.tender.title}" was not selected.',
                tender_title=b.tender.title,
                bid_title=b.title
            )
            for b in other_bids
        ]
        Notification.objects.bulk_create(notifications)
      

        return Response({
            "message": "Bid accepted"
        })


class RejectBidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, bid_id):

        try:
            bid = Bid.objects.get(id=bid_id)

        except Bid.DoesNotExist:
            return Response(
                {"error": "Bid not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # check if current user owns the tender
        if bid.tender.user != request.user:
            return Response(
                {"error": "You do not own this tender"},
                status=status.HTTP_403_FORBIDDEN
            )

        if Bid.objects.filter(tender=bid.tender, status__name="Awarded").exists():
            return Response({"error": "Tender already finalized"})
        
        if bid.status.name == "Awarded":
            return Response({"error": "Cannot reject an accepted bid"})
        
        if bid.status.name == "Rejected":
            return Response({"error": "Bid already rejected"})
        
        
        rejected_status = Status.objects.get(name="Rejected")
        bid.status = rejected_status
        
        try:
            Notification.objects.create(
                recipient=bid.user,
                sender=request.user,
                notification_type="bid_rejected",
                message=f'Your bid for "{bid.tender.title}" was rejected.',
                tender_title=bid.tender.title,
                bid_title=bid.title
            )
        except Exception as e:
            print(e)
            return Response({"error": str(e)})
        
        bid.save()


        return Response({
            "message": "Bid rejected"
        })




class NotificationViewSet(viewsets.ModelViewSet):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')
    