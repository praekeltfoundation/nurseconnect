FROM praekeltfoundation/django-bootstrap:py2

COPY . /app
RUN pip install -e .

ENV DJANGO_SETTINGS_MODULE "nurseconnect.settings.production"
RUN apt-get-install.sh libjpeg-dev redis-server
RUN django-admin collectstatic --noinput
CMD ["nurseconnect.wsgi:application"]
