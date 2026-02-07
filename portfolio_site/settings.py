"""
Django settings for portfolio_site project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load secrets from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECRETS â€” all pulled from .env, never hardcoded
# ============================================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-change-this')

# âš ï¸ IMPORTANT: Remove the hardcoded password!
# The password should ONLY come from .env file
ADMIN_PANEL_PASSWORD = os.environ.get('ADMIN_PANEL_PASSWORD', 'Hisham55@')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'portfolio',

    # Third party
    'rest_framework',
    'corsheaders',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'portfolio_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'portfolio_site.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static_cdn'
STATICFILES_DIRS = [
    BASE_DIR / 'portfolio' / 'static',
]

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# CORS â€” only allow your own domain to hit the API
# ============================================================
# In local dev this is fine. When you deploy, add your real domain:
#   CORS_ALLOWED_ORIGINS = ['https://yourdomain.com']
# ============================================================
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]


# ============================================================
# EMAIL SETTINGS
# ============================================================
# --- FOR LOCAL TESTING (prints emails to terminal) ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- FOR REAL EMAILS (Gmail SMTP) ---
# When you deploy, comment out the console backend above and
# uncomment this block:
#
# EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST         = 'smtp.gmail.com'
# EMAIL_PORT         = 587
# EMAIL_USE_TLS      = True
# EMAIL_HOST_USER    = 'Hishamharismeet@gmail.com'
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# ============================================================

DEFAULT_FROM_EMAIL = 'Hishamharismeet@gmail.com'
ADMIN_EMAIL        = 'Hishamharismeet@gmail.com'


# ============================================================
# SECURITY HEADERS
# ============================================================

# Prevent browsers from guessing content types (stops MIME sniffing attacks)
SECURE_CONTENT_TYPE_NOSNIFF = True

# Tell browsers to use X-XSS-Protection (older browsers)
SECURE_BROWSER_XSS_FILTER = True

# Prevent your site from being loaded inside an iframe (clickjacking)
X_FRAME_OPTIONS = 'DENY'

# Content Security Policy â€” tells the browser exactly what is allowed to run
# This blocks any script/style that isn't explicitly from your approved sources
SECURE_CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "                                          # everything else: only your own domain
    "script-src 'self' 'unsafe-inline' "                            # your own JS + inline scripts
        "https://cdn.jsdelivr.net "                                 # Bootstrap JS
        "https://unpkg.com "                                        # AOS
        "https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js; "  # Particles
    "style-src 'self' 'unsafe-inline' "                             # your own CSS + inline styles
        "https://cdn.jsdelivr.net "                                 # Bootstrap CSS
        "https://unpkg.com "                                        # AOS CSS
        "https://fonts.googleapis.com; "                            # Google Fonts CSS
    "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net data:; "                   # Google Fonts files + Bootstrap Icons
    "img-src 'self' https://images.unsplash.com data:; "            # your images + unsplash placeholders
    "connect-src 'self'; "                                          # AJAX only to your own domain
    "frame-ancestors 'none'; "                                      # no iframes embedding you (same as X-Frame-Options)
)


# ============================================================
# HTTPS ENFORCEMENT
# ============================================================
# These are all OFF by default so local dev (http://localhost)
# keeps working. When you deploy to a real domain with HTTPS,
# flip them all to True.
# ============================================================

# Force all traffic to HTTPS
SECURE_SSL_REDIRECT = False  # â†’ True in production

# Tell browsers to only send cookies over HTTPS
SESSION_COOKIE_SECURE = False  # â†’ True in production
CSRF_COOKIE_SECURE    = False  # â†’ True in production

# HSTS: tell browsers to remember "always use HTTPS" for 1 year
SECURE_HSTS_SECONDS = 0  # â†’ 31536000 in production (1 year)
SECURE_HSTS_INCLUDE_SUBDOMAINS = False  # â†’ True in production
SECURE_HSTS_PRELOAD = False  # â†’ True in production


# ============================================================
# SESSION COOKIE HARDENING
# ============================================================

# Cookie name â€” change from default "sessionid" so scanners can't
# fingerprint your stack as easily
SESSION_COOKIE_NAME = '_ph_sess'

# Prevent JavaScript from reading the session cookie
SESSION_COOKIE_HTTPONLY = True

# Only send the cookie on same-site requests (blocks CSRF from other domains)
SESSION_COOKIE_SAMESITE = 'Lax'

# Session expires when the browser closes (unless "remember me" sets expiry)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#DataBase

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
