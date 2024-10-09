from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegistrationView, subscribe, edit_subscription, delete_subscription, subscription_list


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('subscribe/', subscribe, name='subscribe'),
    path('edit-subscription/<int:subscription_id>/', edit_subscription, name='edit_subscription'),
    path('delete-subscription/<int:subscription_id>/', delete_subscription, name='delete_subscription'),
    path('subscription-list/', subscription_list, name='subscription_list'),
]
