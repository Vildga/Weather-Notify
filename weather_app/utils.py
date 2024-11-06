from django.http import HttpResponse
import os
import requests
import csv
import environ

env = environ.Env()
environ.Env.read_env()


def send_mail_view(request):
    from weather_app.tasks import send_notifications
    send_notifications.delay()
    return HttpResponse("sent")


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


def get_weather_for_city(city_name):
    search_query = city_name
    found_cities = perform_search_in_csv(search_query)

    if found_cities:
        city_data = found_cities[0]
        city_name = city_data['city_name']
        url_weather = f'https://api.weatherbit.io/v2.0/current?city={city_name}&key={env("WEATHER_API_KEY")}'
        response = requests.get(url_weather)
        weather_data = response.json()

        if 'data' in weather_data and weather_data['data']:
            temperature = weather_data['data'][0]['temp']
            description = weather_data['data'][0]['weather']['description']
            return {'city_data': city_data, 'temperature': temperature, 'description': description}
        else:
            return None


