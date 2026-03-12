from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': env.db('DATABASE_URL')  # Railway
}

CORS_ALLOW_ALL_ORIGINS = True