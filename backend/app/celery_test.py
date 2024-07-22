from celery import Celery

celery_app = Celery(
    'test',
    backend='redis://localhost:6379/0',
    broker='redis://localhost:6379/0'
)

@celery_app.task
def test_task():
    return 'Hello, Celery!'
