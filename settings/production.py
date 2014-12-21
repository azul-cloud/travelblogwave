from .staging import *


# Allow all host headers

MAILGUN_SERVER_NAME = 'travelblogwave.com'

DEBUG = True
TEMPLATE_DEBUG = True

if DEBUG:
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'static'),
    )
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

AWS_STORAGE_BUCKET_NAME = 'travelblogwave.media'