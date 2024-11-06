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


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('api_get_weather/', views.api_get_weather, name='api_get_weather_for_subscribed_cities'),
    path('city_weather/', views.city_weather, name='city_weather'),
    path('api/get-weather/<str:city_name>/', views.api_get_weather, name='get_weather_by_city'),
    path('registration/', views.register, name='registration'),
    path('login/', views.user_login, name='login'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('logout/', views.logout_view, name='logout'),
    re_path(r'^webpush/', include('webpush.urls')),
    path('subscription-list/', views.subscription_list, name='subscription_list'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('edit-subscription/<int:subscription_id>/', views.edit_subscription, name='edit_subscription'),
    path('delete-subscription/<int:subscription_id>/', views.delete_subscription, name='delete_subscription'),
]
