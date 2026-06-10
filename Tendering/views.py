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
from django.db.models import Count, Avg, Sum, Q
from .models import User, Tender, Bid, Category, Status
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.core.mail import send_mail
from .models import OTP

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
        if self.request.user.is_staff:
            return User.objects.all()
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

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def verify(self, request, pk=None):
        user = self.get_object()
        user.is_verified = True
        user.save()
        return Response({"status": "user verified"})


class IsVerifiedUser(BasePermission):
    def h_permission(self, request, view):
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

    def get_queryset(self):
        user = self.request.user
        queryset = Tender.objects.all()
        results = self.request.query_params.get('results')

        if results == 'true':
            return queryset.filter(
                Q(is_approved=True) & 
                (Q(status__name__in=["Awarded", "Closed"]) | Q(deadline__lte=timezone.now()))
            ).select_related('category', 'currency', 'location', 'status').prefetch_related('attachments')

        if user.is_staff:
            return queryset.select_related('category', 'currency', 'location', 'status').prefetch_related('attachments')
            
        return queryset.filter(
            is_approved=True,
            deadline__gt=timezone.now()
        ).exclude(status__name__in=["Awarded", "Closed"]).select_related('category', 'currency', 'location', 'status').prefetch_related('attachments')

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        tender = self.get_object()
        tender.is_approved = True
        tender.save()
        return Response({"status": "tender approved"})


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

    def get_queryset(self):
        user = self.request.user
        received = self.request.query_params.get('received')
        if received == 'true':
            return Bid.objects.filter(tender__user=user, status__name="Pending").select_related('tender', 'status', 'user').prefetch_related('documents')
        
        if user.is_staff:
            return Bid.objects.all()
        return Bid.objects.filter(user=user).select_related('tender', 'status', 'user').prefetch_related('documents')

    def perform_create(self, serializer):
        pending_status, _ = Status.objects.get_or_create(name="Pending")
        bid = serializer.save(user=self.request.user, status=pending_status)

        Notification.objects.create(
            recipient=bid.tender.user,
            sender=self.request.user,
            notification_type="new_bid",
            message=f'New bid submitted for "{bid.tender.title}"',
            tender_title=bid.tender.title,
            bid_title=bid.title
        )


class BidDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = BidDocument.objects.all()
    serializer_class = BidDocumentSerializer


class SavedTenderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SavedTender.objects.all()
    serializer_class = SavedTenderSerializer

    def destroy(self, request, *args, **kwargs):
        tender_id = kwargs.get('pk')
        try:
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

        if bid.tender.user != request.user:
            return Response(
                {"error": "You do not own this tender"},
                status=status.HTTP_403_FORBIDDEN
            )

        awarded_status, _ = Status.objects.get_or_create(name="Awarded")
        rejected_status, _ = Status.objects.get_or_create(name="Rejected")

        if Bid.objects.filter(tender=bid.tender, status=awarded_status).exists():
            return Response({"error": "Tender already finalized"})

        if bid.status == rejected_status:
            return Response({"error": "Cannot accept a rejected bid"})

        if bid.status == awarded_status:
            return Response({"error": "Bid already accepted"})

        bid.status = awarded_status
        bid.save()

        other_bids = Bid.objects.filter(
            tender=bid.tender
        ).exclude(id=bid.id)

        other_bids.update(status=rejected_status)

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

        if bid.tender.user != request.user:
            return Response(
                {"error": "You do not own this tender"},
                status=status.HTTP_403_FORBIDDEN
            )

        awarded_status, _ = Status.objects.get_or_create(name="Awarded")
        rejected_status, _ = Status.objects.get_or_create(name="Rejected")

        if Bid.objects.filter(tender=bid.tender, status=awarded_status).exists():
            return Response({"error": "Tender already finalized"})

        if bid.status == awarded_status:
            return Response({"error": "Cannot reject an accepted bid"})

        if bid.status == rejected_status:
            return Response({"error": "Bid already rejected"})

        bid.status = rejected_status
        bid.save()

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
            return Response({"error": str(e)})

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


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_users = User.objects.count()
        unverified_users = User.objects.filter(is_verified=False).count()

        total_tenders = Tender.objects.count()
        pending_approval_tenders = Tender.objects.filter(is_approved=False).count()

        total_bids = Bid.objects.count()

        category_breakdown = Category.objects.annotate(
            tender_count=Count('tender')
        ).values('name', 'tender_count')

        status_breakdown = Bid.objects.values('status__name').annotate(
            count=Count('id')
        )

        avg_bid_value = Bid.objects.aggregate(avg_price=Avg('total_price'))['avg_price'] or 0
        total_tender_budget = Tender.objects.aggregate(total_max=Sum('budget_max'))['total_max'] or 0

        recent_tenders = Tender.objects.order_by('-start_date')[:5].values('id', 'title', 'start_date', 'is_approved')
        recent_bids = Bid.objects.order_by('-creation_date')[:5].values('id', 'title', 'total_price', 'status__name')

        return Response({
            "metrics": {
                "total_users": total_users,
                "unverified_users": unverified_users,
                "total_tenders": total_tenders,
                "pending_approval_tenders": pending_approval_tenders,
                "total_bids": total_bids,
                "average_bid_value": round(float(avg_bid_value), 2),
                "total_tender_budget": float(total_tender_budget),
            },
            "charts": {
                "categories": list(category_breakdown),
                "bid_statuses": list(status_breakdown),
            },
            "recent_activity": {
                "tenders": list(recent_tenders),
                "bids": list(recent_bids),
            }
        })
        

class AdminDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.is_staff:
            return HttpResponse("Unauthorized", status=403)
            
        total_users = User.objects.count()
        unverified_users = User.objects.filter(is_verified=False).count()
        total_tenders = Tender.objects.count()
        total_bids = Bid.objects.count()

        pending_users = User.objects.filter(is_verified=False).select_related('company', 'company__location', 'company__category')
        pending_tenders = Tender.objects.filter(is_approved=False).select_related('user', 'category', 'currency', 'location', 'status').prefetch_related('attachments')
        awarded_bids = Bid.objects.filter(status__name="Awarded").select_related('tender', 'tender__user', 'tender__currency', 'user')
        pending_bids = Bid.objects.filter(status__name="Pending").select_related('tender', 'tender__currency', 'user')

        categories = Category.objects.annotate(count=Count('tender'))
        category_names = [c.name for c in categories]
        category_counts = [c.count for c in categories]

        bid_statuses = Bid.objects.values('status__name').annotate(count=Count('id'))
        status_names = [item['status__name'] for item in bid_statuses]
        status_counts = [item['count'] for item in bid_statuses]

        context = {
            "metrics": {
                "total_users": total_users,
                "unverified_users": unverified_users,
                "total_tenders": total_tenders,
                "total_bids": total_bids,
            },
            "pending_users": pending_users,
            "pending_tenders": pending_tenders,
            "pending_bids": pending_bids,
            "awarded_bids": awarded_bids,
            "chart_data": {
                "category_names": category_names,
                "category_counts": category_counts,
                "status_names": status_names,
                "status_counts": status_counts,
            }
        }
        return render(request, "dashboard.html", context)


class VerifyUserHTMXView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        if not request.user.is_staff:
            return HttpResponse(status=403)
        try:
            user = User.objects.get(id=user_id)
            user.is_verified = True
            user.save()
            return render(request, "partials/user_row_verified.html")
        except User.DoesNotExist:
            return HttpResponse(status=404)


class RejectUserHTMXView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        if not request.user.is_staff:
            return HttpResponse(status=403)
        try:
            user = User.objects.get(id=user_id)
            company = user.company
            if company:
                company.delete()
            else:
                user.delete()
            return HttpResponse("")
        except User.DoesNotExist:
            return HttpResponse(status=404)


class ApproveTenderHTMXView(LoginRequiredMixin, View):
    def post(self, request, tender_id):
        if not request.user.is_staff:
            return HttpResponse(status=403)
        try:
            tender = Tender.objects.get(id=tender_id)
            tender.is_approved = True
            tender.save()
            return render(request, "partials/tender_row_approved.html")
        except Tender.DoesNotExist:
            return HttpResponse(status=404)


class RejectTenderHTMXView(LoginRequiredMixin, View):
    def post(self, request, tender_id):
        if not request.user.is_staff:
            return HttpResponse(status=403)
        try:
            tender = Tender.objects.get(id=tender_id)
            tender.delete()
            return HttpResponse("")
        except Tender.DoesNotExist:
            return HttpResponse(status=404)


class SendOTPView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        code = OTP.generate_code()

        OTP.objects.create(
            user=user,
            code=code
        )

        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP code is: {code}",
            from_email="your_email@gmail.com",
            recipient_list=[email],
            fail_silently=False
        )

        return Response({
            "message": "OTP sent successfully"
        })


class VerifyOTPView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email")
        code = request.data.get("code")

        try:
            user = User.objects.get(email=email)

            otp = OTP.objects.filter(
                user=user,
                code=code,
                is_verified=False
            ).latest('created_at')

        except Exception:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp.is_verified = True
        otp.save()

        user.is_verified = True
        user.save()

        return Response({
            "message": "OTP verified successfully"
        })