from pathlib import Path
import os
import dj_database_url

# --------------------------------------
# BASE DIRECTORY
# --------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------
# SECRET & DEBUG
# --------------------------------------
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-q!sk&q0je5baf*!!$3f&p9pa)eu!q20u#f&9%moj-go(3w0k3-"
)
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"  # False in production

# --------------------------------------
# ALLOWED HOSTS
# --------------------------------------
ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1,maiden-backend.onrender.com"
).split(",")

# --------------------------------------
# INSTALLED APPS
# --------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "core",
]

# --------------------------------------
# MIDDLEWARE
# --------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------------
# URLS & TEMPLATES
# --------------------------------------
ROOT_URLCONF = "maiden.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "maiden.wsgi.application"

# --------------------------------------
# DATABASE
# --------------------------------------
DATABASES = {
    "default": dj_database_url.parse(
        os.getenv(
            "DATABASE_URL",
            "postgresql://neondb_owner:npg_KSL4en3qpXAj@ep-holy-morning-adzqe1nq-pooler.c-2.us-east-1.aws.neon.tech/maiden-database?sslmode=require&channel_binding=require",
        ),
        conn_max_age=600,
        ssl_require=True,
    )
}

# --------------------------------------
# AUTH USER MODEL
# --------------------------------------
AUTH_USER_MODEL = "core.User"

# --------------------------------------
# PASSWORD VALIDATORS
# --------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------
# AUTH BACKENDS
# --------------------------------------
AUTHENTICATION_BACKENDS = [
    "core.auth_backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# --------------------------------------
# INTERNATIONALIZATION
# --------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------
# STATIC FILES
# --------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# --------------------------------------
# DEFAULT AUTO FIELD
# --------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------
# CSRF & CORS
# --------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://maiden-backend.onrender.com",
    "https://maiden-kappa.vercel.app",
    "http://localhost:3000",
]

CORS_ALLOWED_ORIGINS = [
    "https://maiden-backend.onrender.com",
    "https://maiden-kappa.vercel.app",
    "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS"]
CORS_ALLOW_HEADERS = ["Content-Type", "X-CSRFToken", "Cookie", "Authorization"]

# --------------------------------------
# SESSION & COOKIE SETTINGS
# --------------------------------------
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Only use secure cookies in production
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Cross-site cookie behavior
SESSION_COOKIE_SAMESITE = 'Lax' if DEBUG else 'None'

# Redirect HTTP to HTTPS in production
SECURE_SSL_REDIRECT = not DEBUG
