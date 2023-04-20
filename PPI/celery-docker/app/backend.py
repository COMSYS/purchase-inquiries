import celery


app_seller = celery.Celery()
app_seller.autodiscover_tasks(['app.Seller'])

app_buyer = celery.Celery()
app_buyer.autodiscover_tasks(['app.Buyer'])

app_thirdparty = celery.Celery()
app_thirdparty.autodiscover_tasks(['app.ThirdParty'])
