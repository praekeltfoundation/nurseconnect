nurseconnect
=========================

This is an application scaffold for Molo_.

Getting started
---------------

To get started::

    $ virtualenv ve
    $ pip install -e .
    $ ./manage.py migrate
    $ ./manage.py createsuperuser
    $ ./manage.py runserver

You can now connect access the demo site on http://localhost:8000

.. _Molo: https://molo.readthedocs.org


The FED folder is currently derelict and only to be used as a point of reference for styling.
All styles and fed stack have been integrated into the project at `mothership/static/src` and get built to `mothership/static/dist`
django compressor is not being used for the client side fed stack.
