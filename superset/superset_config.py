import os

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{os.getenv('DATABASE_USER', 'postgres')}:"
    f"{os.getenv('DATABASE_PASSWORD', 'postgres')}@"
    f"{os.getenv('DATABASE_HOST', 'postgres')}:"
    f"{os.getenv('DATABASE_PORT', '5432')}/"
    f"{os.getenv('DATABASE_DB', 'superset')}"
)

RESULTS_BACKEND = None

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

class CeleryConfig:  # noqa: D101
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
    task_annotations = {"sql_lab.get_sql_results": {"rate_limit": "100/s"}}
    task_track_started = True
    worker_prefetch_multiplier = 10


CELERY_CONFIG = CeleryConfig
