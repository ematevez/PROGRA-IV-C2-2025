from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-3z7-*mm6rwki_2vx%7yt+!q83utn^kjwx1m^5u)(iq@qa9rm&a'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = env("DEBUG", default=True)
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition
BASICS = ['django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.sites",    ]

TERCEROS = [ # Terceros
    "allauth",                        # núcleo
    "allauth.account",                # cuentas locales (si querés)
    "allauth.socialaccount",          # social login
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",]

PROPIAS = [ # Apps propias  
    "core",  
    "market",
    "market_ai",  
    "perfil",
    "presence",
    "simple_chat",
    "quotes",]

INSTALLED_APPS = BASICS + TERCEROS + PROPIAS




SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
ACCOUNT_SIGNUP_FIELDS = ["email", "username", "password1", "password2"]
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
# (opcional) Config de allauth
ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
# ACCOUNT_EMAIL_VERIFICATION = "optional"

#CONFIGURACION PARA QUE SOLO DURE 30 MIN SIN ACTIVIDAD
SESSION_COOKIE_AGE = 30 * 60           # 30 minutos (en segundos)
SESSION_SAVE_EVERY_REQUEST = True      # cada request renueva el tiempo
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware", #<- Para activo
    "presence.middleware.AutoLogoutMiddleware", #<- Para activo
    "presence.middleware.UpdateLastSeenMiddleware" #<- Ultmima actividad
]

ROOT_URLCONF = 'myclase.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',  # <-- requerido por allauth
                'django.template.context_processors.csrf', # <-- requerido por seguridad de formularios
            ],
        },
    },
]

WSGI_APPLICATION = 'myclase.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": "857315665458-a92seg0oshg60cm3jpc2dca7p3alp0hc.apps.googleusercontent.com",      # si preferís cargar desde settings en vez de admin
            "secret": "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",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    },
    "github": {
        "APP": {
            "client_id": "Ov23li983lEwpYPXV8yb",
            "secret": "166548efa164a756087f8dc28590a2ff1c93e372",
        },
        "SCOPE": ["user:email"],
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
