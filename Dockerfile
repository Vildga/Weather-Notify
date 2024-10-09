FROM python:3.11.2-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DJANGO_SETTINGS_MODULE=Weather.settings

RUN apt-get update \
  && apt-get install -y build-essential \
  && apt-get install -y libpq-dev \
  && apt-get install -y gettext \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt /requirements.txt
RUN pip install "setuptools<58.0.0"
RUN pip install --no-cache-dir -r /requirements.txt

COPY . /app/

CMD ["sh", "-c", "python manage.py migrate && celery -A Weather.celery beat -l info"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
