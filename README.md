# mailing_service
Django service for controlling automatic mailing


# Quick start with Docker 

1) Open `.env.template` file and fill in your credentials

```
DJANGO_SECRET_KEY="DJANGO KEY HERE"
THIRD_PARTY_JWT_KEY="PROBE API KEY HERE"

DB_HOST="db"
DB_PORT="5432"
POSTGRES_DB="mailing_service"
POSTGRES_USER="USERNAME HERE"
POSTGRES_PASSWORD="PASSWORD HERE"
POSTGRES_HOST_AUTH_METHOD=trust

RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=pass
CELERY_BROKER_URL=amqp://admin:pass@rabbit:5672/
```

2) ```docker-compose up``` in your terminal

3) `localhost:8000` in your browser


# Administration

1) When using docker, Admin user is automatically created. You can change credentials in `app/mailing/management/commands/create_admin.py`. Base credentials are:
- username: admin
- password: 12345


# Fixtures 

1) When using docker, test data is automatically bumped from `app/fixtures/fixture.json`. Once set up, these instances will be initialized:
    - 2 Opeator Objects (Beeline, MTS)
    - 2 Client objects with different operators and phone numbers
    - 1 ClientFilter object 
    - 2 Tag objects


# API 

1) Mailing service provides an open(temporary) API. You can read thorugh Swagger UI documentation at:
    - `localhost:8000/api/v1/docs`


# Celery & RabbitMQ

1) Celery worker and RabbitMQ worker are initialized automatically when using docker. Celery is currently responsible for creating `mailing.Message` objects and sending them to `probe.fbrq.cloud/v1/send/`. The algorithm is following:
    - `mailing.Mailing` object is created.
    - `handle_post_save` signal from `mailing.signals.MailingHandler` is called
        - List of appropriate clients is extracted from `ClientFilter` object 

    - Celery task `create_message_object` is delayed:

        - `mailing.Message` object is created and status `NOT_SENT` is set 
        
        - Sending data to third-party service task `send_message_object` is delayed `INCLUDING CLIENT'S TIMEZONE`:
            - message object is sent to another service
            - if request was sucessful, message status is updated to `SENT`