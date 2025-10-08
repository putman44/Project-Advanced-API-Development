from app import create_app
from app.models import Mechanic, ServiceTicket, db
import unittest
from app.utils.utils import encode_token
from app.tests.helper_function import login_mechanic

# python -m unittest discover -s app/tests


class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app.testing = True

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            self.mechanic = Mechanic(
                name="Taylor",
                email="taylor@gmail.com",
                phone="333-333-2222",
                password="password",
                salary=80000,
            )

            db.session.add(self.mechanic)
            db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        # This cleans up the database after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_mechanic(self):
        mechanic_payload = {
            "email": "fishputman@gmail.com",
            "name": "taylor",
            "phone": "333-333-3322",
            "salary": "23000",
            "password": "password44",
        }

        response = self.client.post("/mechanics/", json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["salary"], 23000)

    def test_login_mechanic(self):
        credentials = {"email": "taylor@gmail.com", "password": "password"}

        response = self.client.post("/mechanics/login", json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "success")

    def test_update_mechanic(self):
        update_payload = {"name": "Jerry"}

        headers = {
            "Authorization": "Bearer "
            + login_mechanic(self.client, email="taylor@gmail.com", password="password")
        }

        response = self.client.put("/mechanics/", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "Jerry")
        self.assertEqual(response.get_json()["email"], "taylor@gmail.com")

    def test_failed_update_mechanic(self):
        update_payload = {"phone": "23"}

        headers = {
            "Authorization": "Bearer "
            + login_mechanic(self.client, email="taylor@gmail.com", password="password")
        }

        response = self.client.put("/mechanics/", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.get_json())
        self.assertIn(
            "Invalid phone number format (XXX-XXX-XXXX)", response.get_json()["phone"]
        )

    def test_get_mechanics(self):
        response = self.client.get("/mechanics/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data[0]["name"], "Taylor")
        self.assertEqual(data[0]["salary"], 80000)

    def test_get_mechanic(self):
        response = self.client.get("/mechanics/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["email"], "taylor@gmail.com")

    def test_get_mechanic_tickets(self):
        headers = {
            "Authorization": "Bearer "
            + login_mechanic(self.client, email="taylor@gmail.com", password="password")
        }
        response = self.client.get("/mechanics/my-tickets", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "You have no service tickets")

    def test_delete_mechanics(self):
        headers = {
            "Authorization": "Bearer "
            + login_mechanic(self.client, email="taylor@gmail.com", password="password")
        }
        response = self.client.delete("/mechanics/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["message"], "Mechanic id: 1, successfully deleted"
        )
