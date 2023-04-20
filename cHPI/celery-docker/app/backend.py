import celery


seller_app = celery.Celery()
seller_app.autodiscover_tasks(['app.Seller'])


buyer_app = celery.Celery()
buyer_app.autodiscover_tasks(['app.Buyer'])

third_app = celery.Celery()
third_app.autodiscover_tasks(['app.ThirdParty'])