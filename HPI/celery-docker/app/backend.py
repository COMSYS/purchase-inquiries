import celery


app_buyer = celery.Celery()
app_buyer.autodiscover_tasks(['app.Buyer'])

app_seller = celery.Celery()
app_seller.autodiscover_tasks(['app.Seller'])