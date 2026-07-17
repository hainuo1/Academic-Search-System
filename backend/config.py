import os
import secrets


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    DB_CONFIG = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': os.environ.get('DB_PASSWORD', 'djj7402531'),
        'database': 'AcademicSearchDB',
        'charset': 'utf8mb4',
        'autocommit': False,
    }
