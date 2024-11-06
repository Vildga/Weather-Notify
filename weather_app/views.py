from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
import os
from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import City, User
import requests
import csv
from rest_framework.response import Response
from .serializers.serializers import  SubscriptionSerializer
from django.contrib.auth.decorators import login_required
from .models import Subscription
from .forms import SubscriptionForm, RegistrationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.utils import timezone
from django.contrib.auth import logout
from .models import Notification
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.decorators import api_view
import environ
from .weather_icons import weather_icon_map
import pytz
from datetime import datetime


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


def home(request):
    return render(request, 'home.html')


def city_weather(request):
    city = request.GET.get('search_query')
    context = {}

    if city:
        weather_api_key = os.getenv('WEATHER_API_KEY')
        url = f'https://api.weatherbit.io/v2.0/current?city={city}&key={weather_api_key}'
        forecast_url = f'https://api.weatherbit.io/v2.0/forecast/daily?city={city}&key={weather_api_key}&days=5'

        response = requests.get(url)
        forecast_response = requests.get(forecast_url)

        if response.status_code == 200 and forecast_response.status_code == 200:
            data = response.json()
            forecast_data = forecast_response.json()

            current_weather_code = data['data'][0]['weather']['code']
            current_time = timezone.now()

            city_timezone = pytz.timezone(data['data'][0]['timezone'])
            sunrise_str = data['data'][0]['sunrise']
            sunset_str = data['data'][0]['sunset']

            sunrise = datetime.strptime(sunrise_str, '%H:%M').replace(
                year=current_time.year, month=current_time.month, day=current_time.day, tzinfo=city_timezone
            )
            sunset = datetime.strptime(sunset_str, '%H:%M').replace(
                year=current_time.year, month=current_time.month, day=current_time.day, tzinfo=city_timezone
            )

            if sunrise <= current_time <= sunset:
                icon_filename = weather_icon_map.get(current_weather_code, {'day': 'default.png'})['day']
            else:
                icon_filename = weather_icon_map.get(current_weather_code, {'night': 'default.png'})['night']

            context['city'] = city
            context['temperature'] = data['data'][0]['temp']
            context['description'] = data['data'][0]['weather']['description']
            context['icon_url'] = f'https://cdn.weatherbit.io/static/img/icons/{icon_filename}'

            forecast = []
            for entry in forecast_data['data']:
                forecast_code = entry['weather']['code']
                forecast_icon_filename = weather_icon_map.get(forecast_code, {'day': 'default.png'})['day']

                day_forecast = {
                    'date': entry['datetime'],
                    'temperature': entry['temp'],
                    'description': entry['weather']['description'],
                    'icon_url': f'https://cdn.weatherbit.io/static/img/icons/{forecast_icon_filename}'
                }
                forecast.append(day_forecast)

            context['forecast'] = forecast
        else:
            context['error'] = "City not found or unable to fetch weather data."

    return render(request, 'city_weather.html', context)


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
        messages.success(request, 'You are already logged in.')
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
                messages.error(request, 'Incorrect login or password.')
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
    return render(request, 'city_weather.html', {'notifications': notifications})


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
            description = weather_data['data'][0]['weather']['description']
            return JsonResponse({'temperature': temperature, 'city': city_name, 'description': description})
        else:
            return JsonResponse({'error': 'Weather data not found for the city'})
    else:
        return JsonResponse({'error': 'City not found'})
