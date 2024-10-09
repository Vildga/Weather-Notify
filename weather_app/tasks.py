from Weather.celery import app
from django.core.mail import send_mail
from django.utils import timezone
from .models import Subscription, Notification, City
from push_notifications.models import APNSDevice
from webpush import send_user_notification
import requests
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .utils import get_weather_for_city

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'w41542720@gmail.com'
EMAIL_PASSWORD = 'kimbhsqkbcuofhox'
EMAIL_USE_TLS = True


@app.task
def send_notifications():
    subscriptions = Subscription.objects.all()

    for subscription in subscriptions:
        last_notification_time = subscription.last_notification_time

        if last_notification_time is None or timezone.now() - last_notification_time >= timezone.timedelta(
                hours=int(subscription.period)):
            weather_data = get_weather_for_city(subscription.city)
            temperature_info = f'The current temperature is {weather_data["temperature"]}°C.' if (
                weather_data) else 'Temperature information not available.'

            if subscription.method == 'email':
                send_email_notification(subscription.user, subscription.city, temperature_info)

            elif subscription.method == 'push':
                send_push_notification(subscription.user, subscription.city, temperature_info)

            elif subscription.method == 'webhook':
                send_webhook_notification(subscription.user, subscription.city, temperature_info)

            if weather_data and 'city_data' in weather_data:
                city_data = weather_data['city_data']
                if city_data:
                    Notification.objects.create(
                        user=subscription.user,
                        city_id=city_data.get('city_id', None),
                        content=f'Weather notification for {subscription.city}. {temperature_info}',
                        timestamp=timezone.now()
                    )
            else:
                print(
                    f"Failed to fetch weather data for {subscription.city}. Check your API key and activation status.")


def send_email_notification(user, city, temperature_info):
    try:
        send_mail(
            'Weather Notification',
            f'Hello {user.username},\n\nThis is a weather notification for {city}.\n{temperature_info}',
            'w41542720@gmail.com',
            [user.email],
            fail_silently=False,
        )
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")


def send_push_notification(user, city, temperature_info):
    payload = {"head": "Weather Notification", "body": f'This is a weather notification for {city}.\n{temperature_info}'}
    send_user_notification(user=user, payload=payload, ttl=1000)


# app.conf.beat_schedule = {
#     'send-notifications': {
#         'task': 'Weather.tasks.send_notifications',
#         'schedule': crontab(),
#     },
# }


def send_webhook_notification(user, city, temperature_info):
    webhook_url = user.webhook_url

    if webhook_url:
        weather_data = get_weather_for_city(city)

        if weather_data:
            payload = {
                "head": "Weather Notification",
                "body": f'Weather notification for {city}. {temperature_info}',
            }
            response = requests.post(webhook_url, json=payload)

            if response.status_code == 200:
                print("Webhook notification sent successfully.")
            else:
                print(f"Failed to send webhook notification. Status code: {response.status_code}")
        else:
            print(f"Weather data not found for {city}.")
    else:
        print("User has no webhook URL.")
