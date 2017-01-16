FROM praekeltfoundation/django-bootstrap:onbuild
ENV DJANGO_SETTINGS_MODULE "nurseconnect.settings.production"
RUN apt-get-install.sh libjpeg-dev redis-server
RUN django-admin collectstatic --noinput
ENV APP_MODULE "nurseconnect.wsgi:application"
