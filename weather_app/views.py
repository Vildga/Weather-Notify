from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

import os
from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import City, WeatherData, DefaultCity, User
from .forms import CitySearchForm
import requests
import csv
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers.serializers import UserSerializer, SubscriptionSerializer
from django.contrib.auth.decorators import login_required
from .models import Subscription
from .forms import SubscriptionForm, RegistrationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.utils import timezone
from django.contrib.auth import logout
from weather_app.tasks import send_notifications, send_notifications
from .models import Notification
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .api import SubscriptionViewSet, UserRegistrationView
from .utils import get_weather_for_city
import environ

env = environ.Env()
environ.Env.read_env()


def perform_search_in_csv(search_query):
    found_cities = []
    csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cities_20000.csv'))

    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)
        for row in csv_reader:
            if search_query.lower() in row[1].lower():
                found_cities.append({
                    'city_id': row[0],
                    'city_name': row[1],
                    'state_code': row[2],
                    'country_code': row[3],
                    'country_full': row[4],
                    'lat': row[5],
                    'lon': row[6],
                })
    return found_cities


def get_weather(request, city_name='Kiev'):
    form = CitySearchForm(request.GET)
    found_cities = []
    temperature = None

    if form.is_valid():
        search_query = form.cleaned_data['search_query']
        found_cities = perform_search_in_csv(search_query)

        if len(found_cities) == 1:
            city_name = found_cities[0]['city_name']
            url = f'https://api.weatherbit.io/v2.0/current?city={city_name}&key={env("WEATHER_API_KEY")}'
            response = requests.get(url)
            data = response.json()
            temperature = data['data'][0]['temp']

    default_cities = DefaultCity.objects.all()

    context = {'temperature': temperature, 'city': city_name, 'default_cities': default_cities, 'form': form,
               'found_cities': found_cities}
    return render(request, 'weather.html', context)


@login_required
def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            return redirect('subscription_list')
    else:
        form = SubscriptionForm()

    return render(request, 'subscribe.html', {'form': form})


@login_required
def edit_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)

    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=subscription)
        if form.is_valid():
            form.save()
            return redirect('subscription_list')
    else:
        form = SubscriptionForm(instance=subscription)

    return render(request, 'edit_subscription.html', {'form': form, 'subscription': subscription})


@login_required
def delete_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    subscription.delete()
    return redirect('subscription_list')


@login_required
def subscription_list(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'subscription_list.html', {'subscriptions': subscriptions})


@api_view(['GET'])
def subscription_list_api(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response(serializer.data)


def user_login(request):
    if request.user.is_authenticated:
        messages.success(request, 'Ви вже увійшли до системи.')
        return redirect('')

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('')
            else:
                messages.error(request, 'Неправильний логін чи пароль.')
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
    }
    return render(request, 'login.html', context)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.last_login = timezone.now()
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('profile', args=[user.username]))
    else:
        form = RegistrationForm()

    return render(request, 'registration.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def show_notifications(request):
    notifications = Notification.objects.all()
    return render(request, 'weather.html', {'notifications': notifications})


def api_get_weather(request):
    search_query = request.GET.get('search_query', '')
    found_cities = perform_search_in_csv(search_query)

    if found_cities:
        city_name = found_cities[0]['city_name']
        url = f'https://api.weatherbit.io/v2.0/current?city={city_name}&key={env("WEATHER_API_KEY")}'
        response = requests.get(url)
        weather_data = response.json()

        if 'data' in weather_data and weather_data['data']:
            temperature = weather_data['data'][0]['temp']
            return JsonResponse({'temperature': temperature, 'city': city_name})
        else:
            return JsonResponse({'error': 'Weather data not found for the city'})
    else:
        return JsonResponse({'error': 'City not found'})


@csrf_exempt
def webhook_receiver(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)

        try:
            data = json.loads(request.body.decode('utf-8'))

            city_name = data.get('city')
            city = get_object_or_404(City, name=city_name)

            notification = Notification.objects.create(
                user=user,
                city=city,
                content=data.get('content'),
            )

            return JsonResponse({'status': 'success', 'notification_id': notification.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Method Not Allowed'}, status=405)

