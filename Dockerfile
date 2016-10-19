FROM praekeltfoundation/django-bootstrap
ENV DJANGO_SETTINGS_MODULE "nurseconnect.settings.production"
RUN apt-get-install.sh libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
RUN django-admin collectstatic --noinput
ENV APP_MODULE "nurseconnect.wsgi:application"
