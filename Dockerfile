ARG MOLO_VERSION=6
FROM praekeltfoundation/molo-bootstrap:${MOLO_VERSION}-py3.6-onbuild

ENV DJANGO_SETTINGS_MODULE=nurseconnect.settings.production \
    CELERY_APP=nurseconnect

RUN django-admin collectstatic --noinput && \
    django-admin compress

CMD ["nurseconnect.wsgi:application", "--timeout", "1800"]
