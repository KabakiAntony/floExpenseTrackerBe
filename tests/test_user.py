import os
import json
from .floBaseTest import FloExpenseBaseTest

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')


class TestUser(FloExpenseBaseTest):
    """ test various actions on the user resource """
    admin = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "username": 'flo'
    }

    def create_admin(self):
        """  admin creating function """
        response = self.client.get(
            '/admin',
            content_type="application/json"
        )
        return response

    def login_admin(self):
        """ signin admin"""
        response = self.client.post(
            '/users/login',
            data=json.dumps(self.admin),
            content_type="application/json"
        )
        return response

    def test_creating_admin(self):
        """ test creating an admin"""
        response = self.create_admin()
        self.assertEqual(response.status_code, 201)

        duplicate_admin_resp = self.create_admin()
        self.assertEqual(duplicate_admin_resp.status_code, 409)

    def test_admin_login(self):
        """" test admin login"""
        response = self.create_admin()
        self.assertEqual(response.status_code, 201)
        
        response = self.login_admin()
        self.assertEqual(response.status_code, 200)







