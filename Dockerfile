ARG MOLO_VERSION=5
FROM praekeltfoundation/molo-bootstrap:${MOLO_VERSION}-onbuild

ENV DJANGO_SETTINGS_MODULE=nurseconnect.settings.production \
    CELERY_APP=nurseconnect

RUN django-admin collectstatic --noinput && \
    django-admin compress

CMD ["nurseconnect.wsgi:application", "--timeout", "1800"]
