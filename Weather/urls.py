"""
URL configuration for Weather project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from weather_app import views
from weather_app.api import SubscriptionViewSet, SubscriptionRetrieveUpdateDestroyView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="Your API description",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api_get_weather/', views.api_get_weather, name='api_get_weather_for_subscribed_cities'),
    path('get_weather/', views.get_weather, name='get_weather'),
    path('api/get-weather/<str:city_name>/', views.get_weather, name='get_weather_by_city'),
    path('api/', include('weather_app.urls')),
    path('registration/', views.register, name='registration'),
    path('login/', views.user_login, name='login'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('logout/', views.logout_view, name='logout'),
    re_path(r'^webpush/', include('webpush.urls')),
    path('api/subscriptions/', SubscriptionViewSet.as_view({'get': 'list', 'post': 'create'}), name='subscription-list-create-api'),
    path('api/subscriptions/<int:pk>/', SubscriptionRetrieveUpdateDestroyView.as_view(), name='subscription-retrieve-update-destroy-api'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
