
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SQLITE
SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# psycopg2
POSTGRESQL = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'Otr_Base_Nueva',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5434',
        'ATOMIC_REQUESTS': True,
    }
}

# mysqlclient
MYSQL = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db',
        'USER': 'root',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# django-mssql-backend (django 3.0.6)
SQLSERVER = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'db',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'SQL Server Native Client 10.0',
        },
    },
}