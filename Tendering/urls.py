from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from django.conf import settings
from django.conf.urls.static import static

from .views import *
from .views import SendOTPView, VerifyOTPView

router = DefaultRouter()
router.register(r'tenders', TenderViewSet)
router.register(r'saved-tenders', SavedTenderViewSet)
router.register(r'bids', BidViewSet)
router.register(r'bid-documents', BidDocumentViewSet)
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'statuses', StatusViewSet)
router.register(r'currencies', CurrencyViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'tender-attachments', TenderAttachmentViewSet)

urlpatterns = [
    path('login/', EmailTokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('sign-up/', RegisterView.as_view()),
    path('log-out/', LogoutView.as_view()),
    path('bids/<int:bid_id>/accept/', AcceptBidView.as_view()),
    path('bids/<int:bid_id>/reject/', RejectBidView.as_view()),
    path('check-password/', CheckPasswordView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('dashboard/verify-user/<int:user_id>/', VerifyUserHTMXView.as_view(), name='verify_user_htmx'),
    path('dashboard/reject-user/<int:user_id>/', RejectUserHTMXView.as_view(), name='reject_user_htmx'),
    path('dashboard/approve-tender/<int:tender_id>/', ApproveTenderHTMXView.as_view(), name='approve_tender_htmx'),
    path('dashboard/reject-tender/<int:tender_id>/', RejectTenderHTMXView.as_view(), name='reject_tender_htmx'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('', include(router.urls)),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)