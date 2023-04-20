import json
import os
from app.Seller.mainseller import app
import unittest


class TestFrontend(unittest.TestCase):


    def test_all(self):
        self.register_user()


    def setUp(self):

        self.app = app.test_client()





    def register_user(self):
        response = self.app.post(
            '/start',
            data=json.dumps(
                dict(
                    firstname="bob",
                    lastname="testuser",
                    birthday="monday",
                    street="examplestreet",
                    postal="12345",
                    city="aachen",
                    country="germany",
                    password="test",
                    email="bob@testmail.com",
                    gender="male",
                )
            ),
            content_type='application/json'
        )
        result = json.loads(response.data.decode("utf-8"))
        self.assertEqual(result['result'], 'success')

if __name__ == '__main__':
    unittest.main()
