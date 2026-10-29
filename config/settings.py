"""
settings.py is TAKE IT's main settings file.

Django reads this file once when it starts. Anything that changes from one
install to another (passwords, debug mode, addresses) is NOT typed in here.
Instead it is read from the .env file, through os.environ.
"""

# "os" lets Python read environment variables (the values from .env).
import os

# "Path" is a handy tool for building folder paths that work on any computer.
from pathlib import Path

# BASE_DIR is the project's top folder (the one that holds manage.py).
BASE_DIR = Path(__file__).resolve().parent.parent


# ---- Security and debug ----

# The secret key protects logins and forms. It comes from .env.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# DEBUG shows detailed error pages. It is on only when .env says DJANGO_DEBUG=1.
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

# The web addresses TAKE IT will answer to, e.g. "localhost,192.168.1.50".
# .split(",") turns that comma-separated text into a Python list.
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost").split(",")


# ---- Apps ----

# An "app" is one self-contained feature of a Django site.
# These six come with Django: the admin pages, logins, sessions, and so on.
# Our own TAKE IT apps get added to this list as we build them.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # ---- TAKE IT's own apps ----
    "core",  # Organization settings and shared pieces
]

# Middleware are checkpoints every web request passes through, in order.
# They add security headers, remember who is logged in, block forged forms, etc.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# The file that lists every web address (URL) in TAKE IT.
ROOT_URLCONF = "config.urls"

# Templates are the HTML pages. Django looks for them in each app's
# "templates" folder, and in the project-wide "templates" folder.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# The entry point a web server uses to run TAKE IT.
WSGI_APPLICATION = "config.wsgi.application"


# ---- Database ----

# Connect to PostgreSQL, using the name, user and password from .env.
# POSTGRES_HOST is "db": the name of the database container in docker-compose.yml.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": "5432",
    }
}


# ---- Passwords ----

# Rules for login passwords: not too similar to the username, at least
# 8 characters, not a common password, and not only numbers.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---- Language and time ----

LANGUAGE_CODE = "en-us"

# Times are saved in UTC in the database. Each company's own time zone
# will come from its Organization settings later.
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ---- Static files (CSS, JavaScript, images that ship with TAKE IT) ----

STATIC_URL = "static/"


# ---- Media files (files people upload, like the company logo) ----

# The web address uploaded files are shown from, e.g. /media/logos/logo.png.
MEDIA_URL = "media/"

# The folder uploaded files are saved in (kept out of Git by .gitignore).
MEDIA_ROOT = BASE_DIR / "media"


# The type of ID number Django gives every new database record.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
