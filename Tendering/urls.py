from django.urls import path
from .views import LogoutView, RegisterView, UserDetail, UserList, TenderDetail, TenderList, EmailTokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login/', EmailTokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('sign-up/', RegisterView.as_view()),
    path('log-out/', LogoutView.as_view()),
    path('users/', UserList.as_view()),
    path('users/<int:pk>/', UserDetail.as_view()),
    path('tender/', TenderList.as_view()),
    path('tender/<int:pk>/', TenderDetail.as_view()),
]