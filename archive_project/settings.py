from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ── Security ──────────────────────────────────────────────────────────────

# SECRET_KEY must be set via environment variable — never hard-coded.
SECRET_KEY = os.getenv('SECRET_KEY') or os.getenv('SESSION_SECRET')
if not SECRET_KEY:
    raise ValueError(
        "No SECRET_KEY found. Set SECRET_KEY in your .env file or environment variables. "
        "Generate one with: python -c \"from django.core.management.utils import "
        "get_random_secret_key; print(get_random_secret_key())\""
    )

# Read DEBUG from environment; defaults to False for safety.
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# ALLOWED_HOSTS: comma-separated list in env, or '*' for local dev convenience.
_allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(',') if h.strip()]

# CSRF trusted origins — always includes Replit dev domains; additional
# origins (e.g. Render HTTPS URL) can be added via the CSRF_TRUSTED_ORIGINS
# environment variable as a comma-separated list.
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.dev',
    'https://*.repl.co',
]
_csrf_extra = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if _csrf_extra:
    CSRF_TRUSTED_ORIGINS += [o.strip() for o in _csrf_extra.split(',') if o.strip()]


# ── Application definition ────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Cloudinary — must come before 'django.contrib.staticfiles' is processed
    # in production; listed here so it is always available for import.
    'cloudinary_storage',
    'cloudinary',
    'accounts',
    'core',
    'dashboard',
    'documents',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise serves static files efficiently in production.
    # Must be placed directly after SecurityMiddleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'archive_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'archive_project.wsgi.application'


# ── Database ──────────────────────────────────────────────────────────────
# Uses DATABASE_URL (PostgreSQL) only when DEBUG=False (production mode).
# This prevents Replit's automatically injected DATABASE_URL from switching
# the local dev environment away from SQLite — local dev always uses SQLite.
# On Render: DEBUG=False and DATABASE_URL are both set, so PostgreSQL is used.

_database_url = os.getenv('DATABASE_URL')
if _database_url and not DEBUG:
    DATABASES = {
        'default': dj_database_url.config(
            default=_database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ── Password validation ───────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ── Internationalisation ──────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ── Static files ──────────────────────────────────────────────────────────
# WhiteNoise compresses and fingerprints static files for production.

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    # Media uploads: Cloudinary in production (DEBUG=False), local FS in dev.
    # RawMediaCloudinaryStorage (resource_type='raw') is required for arbitrary
    # document files (.pdf, .docx, .xlsx, .zip, etc.).  The default
    # MediaCloudinaryStorage uses resource_type='image' and rejects non-image
    # uploads with a 500 error.
    'default': {
        'BACKEND': (
            'cloudinary_storage.storage.RawMediaCloudinaryStorage'
            if not DEBUG
            else 'django.core.files.storage.FileSystemStorage'
        ),
    },
    # WhiteNoise compresses and fingerprints static files for production.
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


# ── Media files ───────────────────────────────────────────────────────────
# Local dev only — Cloudinary ignores MEDIA_ROOT/MEDIA_URL in production.

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ── Cloudinary ────────────────────────────────────────────────────────────
# Credentials read from environment variables only — never hard-coded.
# Required on Render (production): CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY,
# CLOUDINARY_API_SECRET.

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY':    os.getenv('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET', ''),
}


# ── Misc ──────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/login/'
