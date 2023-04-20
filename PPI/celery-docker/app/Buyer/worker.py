import os
import unittest
from celery import Celery
from app.Buyer.frontend import app as flaskapp


app = Celery(include=('tasks',))
if( True):
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite = loader.discover('Tests')
    unittest.TextTestRunner().run(suite)
flaskapp.debug = False
flaskapp.run()
