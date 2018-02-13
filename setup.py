import codecs
import os

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()

with codecs.open(os.path.join(HERE, 'requirements.txt'), 'rb', 'utf-8') as f:
    install_requires = list(filter(None, f.readlines()))

setup(name='nurseconnect',
      version=read('VERSION'),
      description='nurseconnect',
      long_description=read('README.rst'),
      classifiers=[
          'Framework :: Django',
          'License :: OSI Approved :: BSD License',
          "Programming Language :: Python",
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Praekelt.org',
      author_email='dev@praekelt.org',
      url='http://github.com/praekeltfoundation/nurseconnect',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={})
