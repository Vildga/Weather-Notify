from django.test import TestCase, Client
from django.utils import timezone
from .models import User, Subscription, City, WeatherData, Notification, DefaultCity
import json
from django.urls import reverse


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user', password='test_password')
        self.city = City.objects.create(name='Test City')
        self.default_city = DefaultCity.objects.create(name='Default City')

    def test_subscription_model(self):
        subscription = Subscription.objects.create(
            user=self.user,
            city=self.city,
            period='1',
            method='email',
            last_notification_time=timezone.now()
        )
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.city, self.city)
        self.assertEqual(subscription.period, '1')
        self.assertEqual(subscription.method, 'email')
        self.assertIsNotNone(subscription.last_notification_time)

    def test_weather_data_model(self):
        weather_data = WeatherData.objects.create(
            city=self.city,
            temperature=25.5,
            humidity=50.0,
            timestamp=timezone.now()
        )
        self.assertEqual(weather_data.city, self.city)
        self.assertEqual(weather_data.temperature, 25.5)
        self.assertEqual(weather_data.humidity, 50.0)
        self.assertIsNotNone(weather_data.timestamp)

    def test_notification_model(self):
        notification = Notification.objects.create(
            user=self.user,
            city=self.city,
            content='Test Notification',
            timestamp=timezone.now()
        )
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.city, self.city)
        self.assertEqual(notification.content, 'Test Notification')
        self.assertIsNotNone(notification.timestamp)

    def test_default_city_model(self):
        default_city = DefaultCity.objects.get(name='Default City')
        self.assertEqual(default_city.name, 'Default City')

    def test_user_model(self):
        user = User.objects.get(username='test_user')
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.jwt_token, '')

    def tearDown(self):
        self.user.delete()
        self.city.delete()
        self.default_city.delete()


class ViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.subscription = Subscription.objects.create(user=self.user, city='TestCity', period='1', method='email')

    def test_get_weather_view(self):
        response = self.client.get(reverse('get_weather'))
        self.assertEqual(response.status_code, 200)

    def test_subscribe_view(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.post(reverse('subscribe'), {'city': 'TestCity', 'period': '1', 'method': 'email'})
        self.assertEqual(response.status_code, 302)

    def test_subscription_list_view(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('subscription_list'))
        self.assertEqual(response.status_code, 200)

    def test_edit_subscription_view(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('edit_subscription', args=[self.subscription.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_subscription_view(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('delete_subscription', args=[self.subscription.id]))
        self.assertEqual(response.status_code, 302)

    def test_api_get_weather_view(self):
        data = {'search_query': 'Kiev'}
        response = self.client.post(reverse('api_get_weather'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertIn('temperature', json_response)
        self.assertIn('city', json_response)

    def tearDown(self):
        self.client.logout()
        self.user.delete()
        self.subscription.delete()