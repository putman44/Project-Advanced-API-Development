from app import create_app
from app.models import Mechanic, Inventory, ServiceTicket, db, Customer
import unittest
from app.tests.helper_function import login_mechanic, login_customer

# python -m unittest discover -s app/tests


class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app.testing = True

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            # Create mechanic, customer, inventory
            mechanic = Mechanic(
                name="Taylor",
                email="taylor@gmail.com",
                phone="333-333-2222",
                password="password",
                salary=80000,
            )
            customer = Customer(
                name="Phil",
                email="phil@gmail.com",
                phone="333-333-2222",
                password="password",
            )
            inventory_part = Inventory(part_name="Headlights", price=59.99, quantity=20)

            db.session.add_all([mechanic, customer, inventory_part])
            db.session.commit()

            # Store IDs and other plain attributes
            self.mechanic_id = mechanic.id
            self.mechanic_email = mechanic.email
            self.mechanic_password = mechanic.password
            self.customer_id = customer.id
            self.customer_email = customer.email
            self.customer_password = customer.password
            self.inventory_part_id = inventory_part.id
            self.inventory_part_name = inventory_part.part_name

            # Create service tickets
            service_ticket_1 = ServiceTicket(
                customer_id=customer.id,
                VIN="1HGCM82633A123456",
                service_date="2030-12-10",
                service_desc="needs a tire rotation",
                mechanics=[mechanic],
            )
            service_ticket_2 = ServiceTicket(
                customer_id=customer.id,
                VIN="1HGCM82633A000000",
                service_date="2030-12-10",
                service_desc="engine is stalling",
                mechanics=[mechanic],
            )

            db.session.add_all([service_ticket_1, service_ticket_2])
            db.session.commit()

            # Store their IDs
            self.service_ticket_id_1 = service_ticket_1.id
            self.service_ticket_id_2 = service_ticket_2.id

        self.client = self.app.test_client()

    def tearDown(self):
        # Clean up database after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_service_ticket(self):
        service_ticket_payload = {
            "customer_id": self.customer_id,
            "VIN": "1HGCM82633A123456",
            "service_date": "2025-12-10",
            "service_desc": "balance all four tires",
            "mechanic_ids": [self.mechanic_id],
        }

        headers = {
            "Authorization": "Bearer "
            + login_mechanic(
                self.client, email=self.mechanic_email, password=self.mechanic_password
            )
        }

        response = self.client.post(
            "/service_tickets/", json=service_ticket_payload, headers=headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["VIN"], "1HGCM82633A123456")

    def test_create_service_ticket_as_customer(self):
        service_ticket_payload = {
            "customer_id": self.customer_id,
            "VIN": "1HGCM82633A1234544",
            "service_date": "2025-12-10",
            "service_desc": "needs new tires",
            "mechanic_ids": [self.mechanic_id],
        }

        headers = {
            "Authorization": "Bearer "
            + login_customer(
                self.client, email=self.customer_email, password=self.customer_password
            )
        }

        response = self.client.post(
            "/service_tickets/", json=service_ticket_payload, headers=headers
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["message"], "Forbidden: insufficient role")

    def test_get_service_tickets(self):
        headers = {
            "Authorization": "Bearer "
            + login_mechanic(
                self.client, email=self.mechanic_email, password=self.mechanic_password
            )
        }

        response = self.client.get("/service_tickets/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["VIN"], "1HGCM82633A123456")

    def test_get_service_ticket(self):
        headers = {
            "Authorization": "Bearer "
            + login_mechanic(
                self.client, email=self.mechanic_email, password=self.mechanic_password
            )
        }

        response = self.client.get(
            f"/service_tickets/{self.service_ticket_id_2}", headers=headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["service_desc"], "engine is stalling")

    def test_get_mechanic_with_most_service_tickets(self):
        response = self.client.get("/service_tickets/most-tickets")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["email"], self.mechanic_email)

    def test_update_service_ticket_part(self):
        service_ticket_parts_payload = {
            "inventory_id": self.inventory_part_id,
            "quantity_used": 2,
            "quantity_returned": 0,
        }

        headers = {
            "Authorization": "Bearer "
            + login_mechanic(
                self.client, email=self.mechanic_email, password=self.mechanic_password
            )
        }

        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id_2}/update-parts",
            json=service_ticket_parts_payload,
            headers=headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["message"],
            f"{self.service_ticket_id_2} {self.inventory_part_name}(s) added",
        )

    def test_update_service_ticket_mechanics(self):
        service_ticket_mechanics_payload = {
            "add_mechanic_ids": [],
            "remove_mechanic_ids": [self.mechanic_id],
        }

        headers = {
            "Authorization": "Bearer "
            + login_mechanic(
                self.client, email=self.mechanic_email, password=self.mechanic_password
            )
        }

        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id_2}/update-mechanics",
            json=service_ticket_mechanics_payload,
            headers=headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {
                "error": "Cannot remove the last mechanic from service ticket; at least one must remain."
            },
        )

    def test_update_service_ticket_info(self):
        service_ticket_info_payload = {
            "VIN": "1HGCM82633A789101",
            "service_date": "2025-12-12",
            "service_desc": "needs new engine, needs new tires",
        }

        headers = {
            "Authorization": "Bearer "
            + login_mechanic(
                self.client, email=self.mechanic_email, password=self.mechanic_password
            )
        }

        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id_2}/update-info",
            json=service_ticket_info_payload,
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["VIN"], "1HGCM82633A789101")

    def test_update_service_ticket_info_invalid_vin(self):
        service_ticket_info_payload = {
            "VIN": "1HG",
            "service_date": "2025-12-12",
            "service_desc": "needs new engine, needs new tires",
        }

        headers = {
            "Authorization": "Bearer "
            + login_mechanic(
                self.client, email=self.mechanic_email, password=self.mechanic_password
            )
        }

        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id_2}/update-info",
            json=service_ticket_info_payload,
            headers=headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["VIN"],
            ["Invalid VIN. Must be 17 characters (letters/digits, no I, O, Q)"],
        )

    def test_delete_service_ticket(self):
        headers = {
            "Authorization": "Bearer "
            + login_mechanic(
                self.client, email=self.mechanic_email, password=self.mechanic_password
            )
        }
        response = self.client.delete(
            f"/service_tickets/{self.service_ticket_id_2}",
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "message": f"Service ticket {self.service_ticket_id_2} deleted successfully."
            },
        )
