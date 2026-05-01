from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *
router = DefaultRouter()
router.register(r'tenders', TenderViewSet)
router.register(r'fields', FieldViewSet)
router.register(r'saved-tenders', SavedTenderViewSet)
urlpatterns = [
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('sign-up/', RegisterView.as_view()),
    path('log-out/', LogoutView.as_view()),
    path('', include(router.urls)),
]