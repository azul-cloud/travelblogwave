import dj_database_url

from .base import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {}
DATABASES['default'] =  dj_database_url.config()

# Enable Connection Pooling
DATABASES['default']['ENGINE'] = 'django_postgrespool'

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

MAILGUN_ACCESS_KEY = os.environ['MAILGUN_ACCESS_KEY']
MAILGUN_SERVER_NAME = 'sandboxbea330ddebf24842829144f24a61eaa1.mailgun.org'

WEB_ROOT_URL = 'http://test.travelblogwave.com'
