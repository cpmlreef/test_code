from pathlib import Path
from dotenv import load_dotenv
from corsheaders.defaults import default_headers
from celery.schedules import crontab
import os
import datetime
import re
from django.http import HttpResponseForbidden
import warnings

load_dotenv() # Load environment variables from .env file
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable must be set")

# Django's SECRET_KEY is used for cryptographic signing
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")

SMTP2GO_API_KEY = os.getenv('SMTP2GO_API_KEY')
if not SMTP2GO_API_KEY:
    raise ValueError("SMTP2GO_API_KEY environment variable must be set")

ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
if not ENVIRONMENT:
    raise ValueError("ENVIRONMENT environment variable must be set")

REDIS_HOST = os.getenv('REDIS_HOST', 'redis.codedd-prod.svc.cluster.local')
if not REDIS_HOST:
    raise ValueError("REDIS_HOST environment variable must be set")

REDIS_PORT = os.getenv('REDIS_PORT', 6379)
if not REDIS_PORT:
    raise ValueError("REDIS_PORT environment variable must be set")

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
if not REDIS_PASSWORD:
    raise ValueError("REDIS_PASSWORD environment variable must be set")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment-specific settings
if ENVIRONMENT == 'dev':
    # Disable SSL/HTTPS requirements for development
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    # Debug should be True in development
    DEBUG = True
else:
    # Production settings with health check exceptions
    SECURE_SSL_REDIRECT = True
    SECURE_SSL_REDIRECT_EXEMPT = [r'^/health/', r'^/health/live/', r'^/health/ready/']  # Exempt health check URLs
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    DEBUG = False

# DDoS Protection Settings
DDoS_RATE_LIMIT = 1000  # requests per window
DDoS_WINDOW_SIZE = 60  # seconds (increased from 1 second)
DDoS_BLOCK_DURATION = 3600  # 1 hour (fixed from 24 hours)
DDoS_IP_WHITELIST = [
    '127.0.0.1',  # localhost
    '::1',        # IPv6 localhost
    '100.64.41.100',
    '100.64.39.124',
    # Add your trusted IPs here
]
DDoS_IP_BLACKLIST = [
    # Add known malicious IPs here
]
DDoS_USER_AGENT_BLACKLIST = [
    'python-requests',
    'curl',
    'wget',
    'apache-httpclient',
    'java',
    'scrapy',
    'phantomjs',
    'headless',
    'bot',
    'spider',
    'crawler'
]
DDoS_REQUEST_SIZE_LIMIT = 1024 * 1024  # 1MB

ADMINS = [('Camillo', 'cpachmann@gmail.com')] 

ALLOWED_HOSTS = [
    # External domains
    'localhost',
    'codedd.ai',
    'www.codedd.ai',
    'api.codedd.ai',
    'ws.codedd.ai',
    # LoadBalancer IP
    '212.227.139.73',
    # Internal Kubernetes service names
    'django',
    'django-0',
    'django.codedd-dev',
    'django-0.django',
    'django.codedd-dev.svc.cluster.local',
    'django-0.django.codedd-dev.svc.cluster.local',
    # Production Kubernetes service names
    'django.codedd-prod',
    'django-0.django.codedd-prod',
    'django.codedd-prod.svc.cluster.local',
    'django-0.django.codedd-prod.svc.cluster.local',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CORS_ALLOW_HEADERS = list(default_headers) + [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Determine origins based on environment
if ENVIRONMENT == 'dev':
    # Development origins
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Other development-specific origins
    ]
    
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Other development-specific origins
    ]
else:
    # Production origins - ONLY include production domains
    CORS_ALLOWED_ORIGINS = [
        "https://codedd.ai",
        "https://www.codedd.ai",
        "https://api.codedd.ai",
        "https://ws.codedd.ai",
        # Internal cluster IPs if needed
        "http://100.64.41.100:8000",
        "http://100.64.39.124:80"
    ]
    
    CSRF_TRUSTED_ORIGINS = [
        "https://codedd.ai",
        "https://www.codedd.ai",
    ]

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_codedd',
    'corsheaders',
    'csp',
    'auditor',
    'channels',
    'channels_redis',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.celery',
]

class KubernetesHostValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile the regex pattern for pod IPs - cover all private IP ranges
        # This covers 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, and 100.64.0.0/10 (Carrier-grade NAT)
        self.pod_ip_pattern = re.compile(r'^(10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|192\.168\.\d+\.\d+|100\.(6[4-9]|[7-9]\d|1[0-1]\d|12[0-7])\.\d+\.\d+)(?::\d+)?$')
        
        # Also accept any host that ends with .cluster.local or .svc (Kubernetes DNS names)
        self.k8s_dns_pattern = re.compile(r'.*\.(svc|cluster\.local)$')

    def __call__(self, request):
        # Get the host from the request
        host = request.get_host()
                
        # Special handling for health checks to avoid disallowed host errors
        if request.path.startswith('/health/'):
            # For health checks, if it's coming from a Kubernetes IP, allow it
            if self.pod_ip_pattern.match(host):
                # Set to a known allowed host
                request.META['HTTP_HOST'] = 'localhost'
                return self.get_response(request)
        
        # For all other requests, validate normally
        if self.pod_ip_pattern.match(host) or self.k8s_dns_pattern.match(host):
            request.META['HTTP_HOST'] = 'localhost'
            
        return self.get_response(request)

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile patterns for blocked paths
        self.blocked_patterns = [
            r'^/\.env$',
            r'^/\.git',
            r'^/\.htaccess$',
            r'^/wp-',
            r'^/index\.php',
            r'^/phpinfo\.php$',
            r'^/php\.ini$',
            r'^/admin\.php$',
            r'^/administrator',
            r'^/wp-admin',
            r'^/mysql',
            r'^/db\.php$',
            r'^/console',
            r'^/shell',
        ]
        self.patterns = [re.compile(pattern) for pattern in self.blocked_patterns]

    def __call__(self, request):
        # Check if path matches any blocked pattern
        path = request.path.lstrip('/')
        if any(pattern.match(path) for pattern in self.patterns):
            return HttpResponseForbidden('Access Denied')
        return self.get_response(request)

class DatabaseHealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check database connection before processing request
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
        except Exception:
            # If connection is dead, close it so it will be recreated
            connection.close()
        return self.get_response(request)

MIDDLEWARE = [
    'CodeDD.middleware.ddos_protection.DDoSProtectionMiddleware',  # Add DDoS protection first
    'CodeDD.settings.KubernetesHostValidationMiddleware',  # Must be first to catch disallowed hosts
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'CodeDD.settings.SecurityMiddleware',
    'CodeDD.settings.DatabaseHealthCheckMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # Add any custom backends here if needed
]

ROOT_URLCONF = 'CodeDD.urls'
TYPEDB_URI = os.environ.get('TYPEDB_URI', 'typedb://typedb:1729')
TYPEDB_DATABASE = 'CodeDD_prod_1'
TYPEDB_USER = os.environ.get('TYPEDB_USER', 'codedd')
TYPEDB_PASSWORD = os.environ.get('TYPEDB_PASSWORD', 'password')

# Frontend URL Configuration
FRONTEND_URL = os.environ.get('FRONTEND_URL')

#
#TYPEDB_CONFIG = {
#    'uri': os.getenv('TYPEDB_URI', 'typedb+s://localhost:1729' if os.getenv('TYPEDB_TLS_ENABLED', 'True').lower() == 'true' else 'typedb://localhost:1729'),
#    'username': os.getenv('TYPEDB_USER'),
#    'password': os.getenv('TYPEDB_PASSWORD'),
#    'database': os.getenv('TYPEDB_DATABASE', 'CodeDD_prod_1'),
#    'tls_enabled': os.getenv('TYPEDB_TLS_ENABLED', 'True').lower() == 'true',
#    'tls_ca_certificate_path': '/etc/typedb/tls/ca.crt',
#}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
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

WSGI_APPLICATION = 'CodeDD.wsgi.application'
ASGI_APPLICATION = 'CodeDD.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [f"redis://default:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"],
            "capacity": 1500,  # Default capacity for the channel layer
            "expiry": 60,      # Message expiry time in seconds
            "symmetric_encryption_keys": [SECRET_KEY],
            "prefix": "channels:",
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(hours=1),  # 1 hour
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(hours=24),    # 1 day
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,  # Set to False if not using token blacklist
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': JWT_SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    'JTI_CLAIM': 'jti',
    'TOKEN_USER_CLASS': 'rest_framework.authtoken.models.Token',
    
    # Add these settings for better token handling
    'LEEWAY': 60,  # 1 minute leeway for timing checks
    'VERIFY_EXPIRATION': True,
    
    # Explicitly set token serializers
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
    'TOKEN_VERIFY_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenVerifySerializer',
}

# Health check settings
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,    # in MB
}

# Update your healthcheck in docker compose.yml to use both endpoints
HEALTHCHECK_ENDPOINTS = {
    'health': '/health/',
    'liveness': '/health/live/',
}

# Get service type
SERVICE_TYPE = os.environ.get('SERVICE_TYPE', 'django')

LOGS_BASE_DIR = '/app/logs' # Using your existing pattern

# Create log directories - add one for transaction_errors
os.makedirs(os.path.join(LOGS_BASE_DIR, 'django'), exist_ok=True)
os.makedirs(os.path.join(LOGS_BASE_DIR, 'celery'), exist_ok=True)
os.makedirs(os.path.join(LOGS_BASE_DIR, 'audits'), exist_ok=True)
os.makedirs(os.path.join(LOGS_BASE_DIR, 'server_errors'), exist_ok=True)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://default:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1',
        'OPTIONS': {
            'db': '1',
            'pool_class': 'redis.connection.BlockingConnectionPool',
            'retry_on_timeout': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
        }
    }
}

# Audit logging configuration
AUDIT_LOG_BATCH_SIZE = 100
AUDIT_LOG_FLUSH_TIMEOUT = 5  # seconds

# Base logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'verbose': { # Already defined, good.
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'audit_formatter': { # Already defined
            '()': 'django_codedd.logging_handlers.AuditFormatter',
            'format': '[{asctime}] [{levelname}] [{audit_uuid}] {message}',
            'style': '{',
        },
        'transaction_error_formatter': { # NEW FORMATTER
            # Using {module}.{funcName} can be helpful.
            # Ensure correlation_id is passed in 'extra' when logging.
            'format': '{levelname} {asctime} {module}.{function_name} [ErrorID:{correlation_id}] {message}\nPath: {pathname} Line: {lineno}',
            'style': '{',
            # Default values if 'extra' keys are not provided
            'defaults': {
                'correlation_id': 'N/A',
            }
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'audit_file': { # Already defined
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_BASE_DIR, 'audits/audit_chains.log'),
            'formatter': 'audit_formatter',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'mode': 'a',
        },
        'audit_db': { # Already defined
            'class': 'django_codedd.logging_handlers.DatabaseLogHandler',
            'formatter': 'audit_formatter',
            'level': 'INFO', # Assuming INFO is appropriate for DB audit logs
        },
        'transaction_error_file': { # NEW HANDLER for general server errors
            'level': 'ERROR', # Log only ERROR and CRITICAL
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_BASE_DIR, 'server_errors/transaction_errors.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'transaction_error_formatter', # Use the new formatter
        },
        # Your existing django_file and celery_file handlers will be added below based on SERVICE_TYPE
    },
    'loggers': {
        'django': {
            'handlers': ['console'], # Will be appended with django_file later
            'level': 'INFO',
            'propagate': False, # Keep as False if you want Django logs separate
        },
        'celery': { # Already defined
            'handlers': ['console'], # Will be appended with celery_file later
            'level': 'INFO',
            'propagate': False,
        },
        'celery.task': { # Already defined
            'handlers': ['console'], # Will be appended with celery_file later
            'level': 'INFO',
            'propagate': False,
        },
        'auditor': { # Already defined
            'handlers': ['console', 'audit_file', 'audit_db'],
            'level': 'INFO',
            'propagate': False,
        },
        'django_codedd': { # Already defined
            'handlers': ['console', 'audit_file', 'audit_db'], # Consider if all django_codedd logs should go to audit_db
            'level': 'INFO',
            'propagate': False,
        },
        'django_codedd.view_functions.package_dependencies': { # Already defined
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'audit_chain': { # Already defined
            'handlers': ['console', 'audit_file', 'audit_db'],
            'level': 'INFO',
            'propagate': False,
        },
        'server_errors': { # NEW LOGGER for your application's transaction/critical errors
            'handlers': ['transaction_error_file', 'console'], # Log to file and console
            'level': 'ERROR', # Minimum level this logger will handle for these handlers
            'propagate': False, # Set to True if you also want these errors to go to a parent/root logger
                               # e.g., if you have a general 'mail_admins' handler on root.
                               # For now, False to keep it self-contained.
        },
    },
    'root': {
        'handlers': ['console'], # Root logger handler
        'level': 'INFO',         # Default level for unspecified loggers
    },
}

# Create log files if they don't exist
for log_file in ['/app/logs/django/django.log', '/app/logs/celery/celery.log']:
    try:
        with open(log_file, 'a') as f:
            pass
    except Exception:
        pass

# Add file handlers based on service type
if SERVICE_TYPE == 'django':
    LOGGING['handlers']['django_file'] = {
        'class': 'logging.handlers.WatchedFileHandler',
        'filename': '/app/logs/django/django.log',
        'formatter': 'standard',
        'mode': 'a',
    }
    LOGGING['loggers']['django']['handlers'].append('django_file')
elif SERVICE_TYPE == 'celery':
    LOGGING['handlers']['celery_file'] = {
        'class': 'logging.handlers.WatchedFileHandler',
        'filename': '/app/logs/celery/celery.log',
        'formatter': 'standard',
        'mode': 'a',
    }
    LOGGING['loggers']['celery']['handlers'].append('celery_file')
    LOGGING['loggers']['celery.task']['handlers'].append('celery_file')

# Database Configuration
DB_NAME = 'codedd_prod' if ENVIRONMENT == 'prod' else 'codedd'

# Define SSL options based on environment
DB_SSL_MODE = 'disable'

# Define pool options per service type
POOL_OPTIONS = {
    'django': {
        'POOL_SIZE': 5,
        'MAX_OVERFLOW': 2,
        'MAX_CONNS': 7,
        'RECYCLE': 300,
        'TIMEOUT': 30,
    },
    'celery': {
        'POOL_SIZE': 8,
        'MAX_OVERFLOW': 2,
        'MAX_CONNS': 10,
        'RECYCLE': 300,
        'TIMEOUT': 30,
    },
    'celery-beat': {
        'POOL_SIZE': 2,
        'MAX_OVERFLOW': 1,
        'MAX_CONNS': 3,
        'RECYCLE': 300,
        'TIMEOUT': 30,
    }
}.get(SERVICE_TYPE, {  # Default fallback if SERVICE_TYPE not matched
    'POOL_SIZE': 3,
    'MAX_OVERFLOW': 1,
    'MAX_CONNS': 4,
    'RECYCLE': 300,
    'TIMEOUT': 30,
})

# Define logging pool options
LOGGING_POOL_OPTIONS = {
    'POOL_SIZE': 2,
    'MAX_OVERFLOW': 1,
    'MAX_CONNS': 3,
    'RECYCLE': 300,
    'TIMEOUT': 30,
}

DATABASES = {
    'default': {
        'ENGINE': 'django_db_geventpool.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', DB_NAME),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 5,
            'sslmode': DB_SSL_MODE,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'isolation_level': 1,  # READ COMMITTED
            'client_encoding': 'UTF8',
            'application_name': f'CodeDD-{SERVICE_TYPE}',
        },
        'CONN_MAX_AGE': 0,  # Must be 0 when using connection pooling
        'CONN_HEALTH_CHECKS': True,
        'POOL_OPTIONS': POOL_OPTIONS,
        'ATOMIC_REQUESTS': False,
        'AUTOCOMMIT': True,
        'POOL_TIMEOUT': 30,  # Maximum time to wait for a connection from the pool
        'POOL_RECYCLE': 300,  # Recycle connections after 5 minutes
        'POOL_PRE_PING': True,  # Verify connections before using them
    },
    'logging': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Use regular psycopg2 for logging
        'NAME': os.environ.get('POSTGRES_DB', DB_NAME),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 5,
            'sslmode': DB_SSL_MODE,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'isolation_level': 1,  # READ COMMITTED
            'client_encoding': 'UTF8',
            'application_name': f'CodeDD-{SERVICE_TYPE}-logging',
        },
        'CONN_MAX_AGE': 0,
        'CONN_HEALTH_CHECKS': True,
        'POOL_OPTIONS': LOGGING_POOL_OPTIONS,
        'ATOMIC_REQUESTS': False,
        'AUTOCOMMIT': True,
        'POOL_TIMEOUT': 30,
        'POOL_RECYCLE': 300,
        'POOL_PRE_PING': True,
    }
}

# Celery Configuration
CELERY_BROKER_URL = f'redis://default:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://default:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0'

# Basic Celery Settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Worker Settings
CELERY_WORKER_POOL = 'prefork'
CELERY_WORKER_CONCURRENCY = 4
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 50
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 512000
CELERY_WORKER_ENABLE_REMOTE_CONTROL = True
CELERY_WORKER_SEND_TASK_EVENTS = True

# Task Settings
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_CREATE_MISSING_QUEUES = False
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE = 'default'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'default'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 90000
CELERY_TASK_SOFT_TIME_LIMIT = 86400
CELERY_TASK_SEND_SENT_EVENT = True

# Broker Settings
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'confirm_publish': True,
    'max_retries': None,
    'interval_start': 0,
    'interval_step': 1,
    'interval_max': 10,
    'connection_max_retries': None,
    'prefetch_count': 1,
}

# Result Backend Settings
CELERY_RESULT_EXPIRES = 90000
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_PERSISTENT = True

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'remove-expired-audits': {
        'task': 'django_codedd.tasks.remove_expired_audits',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        'args': (),
    },
    'cleanup-audit-logs': {
        'task': 'django_codedd.tasks.cleanup_audit_logs',
        'schedule': crontab(minute=0, hour=3, day_of_week=1),  # Every Monday at 3 AM
        'args': (),
    },
    'monitor-service-health': {
        'task': 'django_codedd.tasks.monitor_service_health',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'args': (),
    },
}

# Celery Beat Settings
DJANGO_CELERY_BEAT_TZ_AWARE = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Queue Definitions are handled in celery.py

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files storage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Create directories if they don't exist
os.makedirs(STATIC_ROOT, exist_ok=True)
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)

# Stripe Settings
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
# Ensure Stripe keys are available
if not STRIPE_SECRET_KEY or STRIPE_SECRET_KEY.startswith('${'):
    warnings.warn("STRIPE_SECRET_KEY is not set properly. Stripe payments will not work.", RuntimeWarning)
    
# Add Content Security Policy settings
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", 'https://js.stripe.com', 'https://cdn.jsdelivr.net')
CSP_STYLE_SRC = ("'self'", 'https://fonts.googleapis.com', "'unsafe-inline'")
CSP_FONT_SRC = ("'self'", 'https://fonts.gstatic.com')
CSP_IMG_SRC = ("'self'", 'data:', 'https:')
CSP_CONNECT_SRC = ("'self'", 'https://api.codedd.ai', 'https://ws.codedd.ai')
CSP_FRAME_SRC = ("'self'", 'https://js.stripe.com')
CSP_INCLUDE_NONCE_IN = ['script-src']
CSP_REPORT_URI = '/csp-report/'

# Set X-Content-Type-Options header
SECURE_CONTENT_TYPE_NOSNIFF = True

# HSTS settings (you already have some of these)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# X-XSS-Protection header (modern browsers use CSP instead, but for older browsers)
SECURE_BROWSER_XSS_FILTER = True

# Disable clickjacking
X_FRAME_OPTIONS = 'DENY'

# Referrer Policy
SECURE_REFERRER_POLICY = 'same-origin'

# Feature Policy (now Permissions Policy)
PERMISSIONS_POLICY = {
    'geolocation': 'none',
    'microphone': 'none',
    'camera': 'none',
    'payment': 'self',
    'accelerometer': 'none',
    'autoplay': 'none',
    'gyroscope': 'none',
    'magnetometer': 'none',
}

