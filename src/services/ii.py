from io import BytesIO
import os
import sys
from dotenv import load_dotenv
import boto3
from fpdf import FPDF
import psycopg2
from datetime import datetime
from random import sample
from settings import config

# Принудительно установим стандартную кодировку UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

# Конфигурация с явным указанием кодировки
DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': 'localhost',
    'port': 5432,
}

MINIO_CONFIG = {
    'endpoint': "http://localhost:9000",
    'access_key': os.getenv('MINIO_ROOT_USER'),
    'secret_key': os.getenv('MINIO_ROOT_PASSWORD'),
    'bucket': 'resume'
}

# Инициализация клиента S3
s3 = boto3.client(
    's3',
    endpoint_url=MINIO_CONFIG['endpoint'],
    aws_access_key_id=MINIO_CONFIG['access_key'],
    aws_secret_access_key=MINIO_CONFIG['secret_key'],
    config=boto3.session.Config(signature_version='s3v4'),
    verify=False
)


def update_db(student_id, resume_url):
    """Обновляет ссылку на резюме в базе данных"""
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE student SET resume_pdf = %s WHERE id = %s",
                    (resume_url, student_id)
                )
                conn.commit()
    except Exception as e:
        print(f"Ошибка обновления базы данных для студента {student_id}: {e}")
        raise

def upload_to_minio(pdf_data, student_id):
    """Загружает PDF в MinIO"""
    try:
        filename = f"student_{student_id}_resume.pdf"

        # Загрузка в MinIO
        s3.upload_fileobj(
            BytesIO(pdf_data),
            MINIO_CONFIG['bucket'],
            filename,
            ExtraArgs={'ContentType': 'application/pdf'}
        )

        # Формируем URL для доступа
        return f"{filename}"
    except Exception as e:
        print(f"Ошибка загрузки в MinIO для студента {student_id}: {e}")
        raise

def main():
    try:
        print("Проверка подключения к MinIO...")
        # Проверка и создание бакета
        buckets = [b['Name'] for b in s3.list_buckets().get('Buckets', [])]
        if MINIO_CONFIG['bucket'] not in buckets:
            s3.create_bucket(Bucket=MINIO_CONFIG['bucket'])
            print(f"Создан бакет {MINIO_CONFIG['bucket']}")
        else:
            print(f"Бакет {MINIO_CONFIG['bucket']} доступен")

        # Проверка подключения к PostgreSQL
        print("Проверка подключения к PostgreSQL...")
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"Подключено к PostgreSQL: {db_version[0]}")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            # Выводим параметры подключения для отладки (без пароля)
            debug_config = DB_CONFIG.copy()
            debug_config.pop('password', None)
            print(f"Параметры подключения: {debug_config}")
            raise

        # Основная обработка
        print("Начало обработки студентов...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, COALESCE(desired_role, 'Backend Developer'), year FROM student")

        for student_id, first_name, last_name, role, year in cursor.fetchall():
            try:
                print(f"Обработка студента {student_id}...")
                pdf_data = generate_pdf(role, first_name, last_name, year)
                resume_pdf = upload_to_minio(pdf_data, student_id)
                update_db(student_id, resume_pdf)
                print(f"Успешно обработан студент {student_id}")
            except Exception as e:
                print(f"Ошибка обработки студента {student_id}: {e}")

        print("Все резюме обработаны")

    except Exception as e:
        print(f"Критическая ошибка: {str(e)[:200]}")
    finally:
        print("Работа завершена")

if __name__ == "__main__":
    main()
