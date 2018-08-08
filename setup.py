from setuptools import setup, find_packages

setup(
    name='placeholder',
    install_requires=['django>=2.1', 'psycopg2-binary>=2.7.5'],
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    url='https://bitbucket.org/jtalowell/placeholder/')
