from app import create_app
from app.models import Mechanic, Inventory, db
import unittest
from app.utils.utils import encode_token
from app.tests.helper_function import login_mechanic

# python -m unittest discover -s app/tests


class TestInventories(unittest.TestCase):
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

            self.inventory_part = Inventory(
                part_name="Headlights", price=59.99, quantity=20
            )
            
            db.session.add_all([self.mechanic, self.inventory_part])
            db.session.commit()
            self.inventory_part_id = self.inventory_part.id

        self.client = self.app.test_client()

    def tearDown(self):
        # This cleans up the database after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_inventory_part(self):
        inventory_part_payload = {
            "part_name": "Front Bumper",
            "price": 200,
            "quantity": 6,
        }
        headers = {
            "Authorization": "Bearer "
            + login_mechanic(self.client, email="taylor@gmail.com", password="password")
        }
        response = self.client.post(
            "/inventories/", json=inventory_part_payload, headers=headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["price"], 200)

    def test_get_inventory_parts(self):
        response = self.client.get("/inventories/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data[0]["part_name"], "Headlights")
        self.assertEqual(data[0]["price"], 59.99)

    def test_get_inventory_part(self):
        part_id = self.inventory_part.id
        response = self.client.get(f"/inventories/{part_id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["quantity"], 20)

    def test_update_inventory_part(self):
        update_payload = {"quantity": 1000}

        headers = {
            "Authorization": "Bearer "
            + login_mechanic(self.client, email="taylor@gmail.com", password="password")
        }
        part_id = self.inventory_part.id
        response = self.client.put(
            f"/inventories/{part_id}", json=update_payload, headers=headers
        )
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["part_name"], "Headlights")
        self.assertEqual(response.get_json()["quantity"], 1000)

    def test_delete_inventory_part(self):
        headers = {
            "Authorization": "Bearer "
            + login_mechanic(self.client, email="taylor@gmail.com", password="password")
        }
        part_id = self.inventory_part.id
        response = self.client.delete(f"/inventories/{part_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["message"], "Successfully deleted part id 1: Headlights"
        )

    def test_delete_non_existent_inventory_part(self):
        headers = {
            "Authorization": "Bearer "
            + login_mechanic(self.client, email="taylor@gmail.com", password="password")
        }
        response = self.client.delete("/inventories/100", headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["message"], "Invalid part id")
