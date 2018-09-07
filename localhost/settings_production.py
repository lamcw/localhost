import os

from localhost.settings import *

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
