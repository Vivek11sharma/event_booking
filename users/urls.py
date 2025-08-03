from django.urls import path
from .views import RegisterView, CustomLoginView, CustomTokenRefreshView, PasswordResetRequestView, PasswordResetConfirmView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/<uuid:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
]
