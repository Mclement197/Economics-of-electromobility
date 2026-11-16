import os
from pathlib import Path
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY=os.environ.get('VOLTO_SECRET_KEY','')
if not SECRET_KEY: raise ImproperlyConfigured('Set VOLTO_SECRET_KEY to a private random value.')
DEBUG=False
DEMO_MODE=os.environ.get('VOLTO_DEMO','0')=='1'
ALLOWED_HOSTS=os.environ.get('VOLTO_HOSTS','localhost,127.0.0.1,testserver').split(',')
CSRF_TRUSTED_ORIGINS=os.environ.get('VOLTO_CSRF_ORIGINS','http://127.0.0.1:18930').split(',')
APP_URL=os.environ.get('VOLTO_APP_URL','http://127.0.0.1:18930')
INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','axes','core']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','core.middleware.PrivateResponses','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware','axes.middleware.AxesMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='config.wsgi.application'
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':os.environ.get('VOLTO_DB',str(BASE_DIR/'private/app.sqlite3')),'OPTIONS':{'timeout':20,'transaction_mode':'IMMEDIATE'}}}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
AUTHENTICATION_BACKENDS=['axes.backends.AxesStandaloneBackend','django.contrib.auth.backends.ModelBackend']
AXES_FAILURE_LIMIT=6
AXES_COOLOFF_TIME=timedelta(minutes=15)
AXES_LOCKOUT_PARAMETERS=[['username','ip_address']]
AXES_RESET_ON_SUCCESS=True
AXES_ENABLED=os.environ.get('VOLTO_AXES','1')=='1'
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':10}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-gb'
TIME_ZONE='Europe/Zurich'
USE_I18N=True
USE_TZ=True
STATIC_URL='/static/'
STATIC_ROOT=Path(os.environ.get('VOLTO_STATIC',str(BASE_DIR/'staticfiles')))
STATICFILES_DIRS=[BASE_DIR/'static']
STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SECURE=os.environ.get('VOLTO_SECURE','0')=='1'
CSRF_COOKIE_SECURE=SESSION_COOKIE_SECURE
SESSION_COOKIE_SAMESITE='Lax'
CSRF_COOKIE_SAMESITE='Lax'
SESSION_COOKIE_AGE=43200
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_REFERRER_POLICY='same-origin'
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
SECURE_HSTS_SECONDS=31536000 if SESSION_COOKIE_SECURE else 0
X_FRAME_OPTIONS='DENY'
LOGIN_URL='/login/'
DATA_UPLOAD_MAX_MEMORY_SIZE=65536
DEFAULT_CHARSET='utf-8'

CSRF_FAILURE_VIEW='core.views.csrf_failure'

SECURE_SSL_REDIRECT=SESSION_COOKIE_SECURE
