import csv
from django.core.management.base import BaseCommand
from weather_app.models import City


class Command(BaseCommand):
    help = 'Imports cities from a CSV file into the weather_app_city table'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file containing city data')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Пропустить заголовки

            for row in reader:
                try:
                    city_id = int(row[0])  # Преобразование city_id в число
                    name = row[1]
                    state_id = int(row[2])  # Преобразование state_id в число
                    country_code = row[3]
                    country = row[4]
                    latitude = float(row[5])  # Преобразование latitude в число с плавающей точкой
                    longitude = float(row[6])  # Преобразование longitude в число с плавающей точкой

                    # Создание или обновление записи в базе данных
                    City.objects.update_or_create(
                        id=city_id,
                        defaults={
                            'name': name,
                            'state_id': state_id,
                            'country_code': country_code,
                            'country': country,
                            'latitude': latitude,
                            'longitude': longitude,
                        }
                    )
                except ValueError as e:
                    self.stdout.write(self.style.WARNING(f"Skipping row due to error: {e}"))

        self.stdout.write(self.style.SUCCESS('Cities imported successfully.'))