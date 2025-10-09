from app import create_app
from app.models import Customer, db
import unittest
from app.tests.helper_function import login_customer

# python -m unittest discover -s app/tests


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app.testing = True

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            self.customer = Customer(
                name="Phil",
                email="phil@gmail.com",
                phone="333-333-2222",
                password="password",
            )

            db.session.add(self.customer)
            db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        # This cleans up the database after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_customer(self):
        customer_payload = {
            "email": "taylor@gmail.com",
            "name": "Taylor",
            "phone": "333-333-4444",
            "password": "password",
        }

        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["name"], "Taylor")

    def test_invalid_creation(self):
        member_payload = {
            "name": "John Doe",
            "phone": "123-456-7890",
            "password": "123",
        }

        response = self.client.post("/customers/", json=member_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["email"], ["Missing data for required field."]
        )

    def test_login_customer(self):
        credentials = {"email": "phil@gmail.com", "password": "password"}

        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "success")

    def test_update_customer(self):
        update_payload = {"name": "Peter"}

        headers = {
            "Authorization": "Bearer "
            + login_customer(self.client, email="phil@gmail.com", password="password")
        }

        response = self.client.put("/customers/", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "Peter")
        self.assertEqual(response.get_json()["email"], "phil@gmail.com")

    def test_get_customers(self):
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("customers", data)
        self.assertEqual(data["customers"][0]["name"], "Phil")

    def test_get_customer(self):
        response = self.client.get("/customers/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["phone"], "333-333-2222")

    def test_get_customer_tickets(self):
        headers = {
            "Authorization": "Bearer "
            + login_customer(self.client, email="phil@gmail.com", password="password")
        }
        response = self.client.get("/customers/my-tickets", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "You have no service tickets")

    def test_delete_customer(self):
        headers = {
            "Authorization": "Bearer "
            + login_customer(self.client, email="phil@gmail.com", password="password")
        }
        response = self.client.delete("/customers/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["message"], "Customer id: 1, successfully deleted"
        )
