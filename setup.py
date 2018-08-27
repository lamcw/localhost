import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

setup(
    name='placeholder',
    install_requires=[
        'django>=2.1', 'psycopg2-binary>=2.7.5', 'Pillow>=5.2.0',
        'django-polymorphic>=2.0.3'
    ],
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    long_description=README,
    url='https://bitbucket.org/jtalowell/placeholder/')
