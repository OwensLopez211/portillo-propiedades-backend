release: python manage.py migrate && python manage.py createsuperuser --no-input --username andres --email owenslopez211@gmail.com
web: gunicorn portillo_propiedades_backend.wsgi --bind 0.0.0.0:$PORT
