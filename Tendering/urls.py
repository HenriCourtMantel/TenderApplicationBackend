from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

router = DefaultRouter()
router.register(r'tenders', TenderViewSet)
router.register(r'saved-tenders', SavedTenderViewSet)
router.register(r'bids', BidViewSet)
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'statuses', StatusViewSet)
router.register(r'currencies', CurrencyViewSet)
router.register(r'locations', LocationViewSet)

urlpatterns = [
    path('login/', EmailTokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('sign-up/', RegisterView.as_view()),
    path('log-out/', LogoutView.as_view()),
    path('bids/<int:bid_id>/accept/', AcceptBidView.as_view()),
    path('', include(router.urls)),  
]
from django.urls import path
from .views import *

urlpatterns = [
    path('check-password/', CheckPasswordView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
]
router.register(r'tender-attachments', TenderAttachmentViewSet)