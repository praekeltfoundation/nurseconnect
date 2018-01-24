NurseConnect MobiSite
=========================
.. image:: https://img.shields.io/travis/praekelt/nurseconnect.svg
        :target: https://travis-ci.org/praekelt/nurseconnect

.. image:: https://coveralls.io/repos/praekelt/nurseconnect/badge.png?branch=develop
    :target: https://coveralls.io/r/praekelt/nurseconnect?branch=develop
    :alt: Code Coverage

NurseConnect is a South African National Department of Health (NDOH) initiative which aims to
support maternal health nurses in the public sector through the use of cell phone based
technologies integrated into maternal and child health services.

The NurseConnect Mobisite is built using Molo_.

Getting started
---------------

To get started::

    $ virtualenv ve
    $ source ve/bin/activate
    $ pip install -e .
    $ ./manage.py migrate
    $ ./manage.py createsuperuser
    $ ./manage.py runserver

You can now connect access the demo site on http://localhost:8000

To download languages, sections, articles and images, navigate to ``/admin/import-site/``
and input the URL of the site that you want to import data from. Do this before any further
setup.

Additional setup:

In order to properly set up the sign up form, create a terms and conditions footer page
and then navigate to ``/admin/settings/profiles/userprofilessettings/`` and under
"Terms and Conditions on Registration", select the page you just created.

Tests
-----

To run tests::

    $ py.test

License
-------
See _License for more detail.

Note
-----

The FED folder is currently derelict and only to be used as a point of reference for styling.
All styles and fed stack have been integrated into the project at `mothership/static/src` and get built to `mothership/static/dist`
django compressor is not being used for the client side fed stack.

.. _Molo: https://molo.readthedocs.org
.. _License: https://github.com/praekelt/nurseconnect/blob/develop/LICENSE
