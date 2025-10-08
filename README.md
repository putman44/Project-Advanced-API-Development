# Mechanic Service API

A RESTful API for managing customers, mechanics, inventory parts, and service tickets built with Flask, SQLAlchemy, and MySQL.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Installation](#installation)
4. [Entity-Relationship-Diagram](#entity-relationship-diagram)
5. [API Endpoints](#api-endpoints)
6. [Swagger UI](#swagger-ui)
7. [Unit Testing](#unit-testing)
8. [Swagger CLI and Nodemon](#swagger-cli-and-nodemon)

---

## Features

- CRUD operations for customers, mechanics, inventories, and service tickets.
- One-to-many relationships (Customer → ServiceTicket).
- Many-to-many relationships with extra data (ServiceTicket ↔ Mechanic via ServiceTicketMechanic).
- Many-to-many relationships (ServiceTicket ↔ Inventory via ServiceTicketInventory).
- Marshmallow schemas for serialization and validation.
- Role-based access control (RBAC) with JWT authentication.
- Rate limiting to prevent abuse and caching.

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** MySQL
- **ORM:** SQLAlchemy
- **Serialization:** Flask-Marshmallow, Marshmallow-SQLAlchemy

---

## Installation

```bash
git clone https://github.com/putman44/Project-Advanced-API-Development
cd Project-Advanced-API-Development.git

python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

pip install Flask Flask-SQLAlchemy Flask-Marshmallow mysql-connector-python marshmallow-sqlalchemy Flask-Limiter Flask-Caching python-jose alembic flask-swagger flask_swagger_ui @apidevtools/swagger-cli nodemon

pip freeze > requirements.txt
```

## Entity-Relationship-Diagram

![Entity Relationship Diagram](Mechanic_Erd.png)

## API Endpoints

### Customers

| Method | Endpoint                           | Description        |
| ------ | ---------------------------------- | ------------------ |
| POST   | /customers                         | Create a customer  |
| GET    | /customers                         | List all customers |
| GET    | /customers/&lt;int:customer_id&gt; | Get a customer     |
| PUT    | /customers/&lt;int:customer_id&gt; | Update a customer  |
| DELETE | /customers/&lt;int:customer_id&gt; | Delete a customer  |

### Mechanics

| Method | Endpoint                           | Description        |
| ------ | ---------------------------------- | ------------------ |
| POST   | /mechanics                         | Create a mechanic  |
| GET    | /mechanics                         | List all mechanics |
| GET    | /mechanics/&lt;int:mechanic_id&gt; | Get a mechanic     |
| PUT    | /mechanics/&lt;int:mechanic_id&gt; | Update a mechanic  |
| DELETE | /mechanics/&lt;int:mechanic_id&gt; | Delete a mechanic  |

### Service Tickets

| Method | Endpoint                                                           | Description                                     |
| ------ | ------------------------------------------------------------------ | ----------------------------------------------- |
| POST   | /service_tickets                                                   | Create a service ticket                         |
| GET    | /service_tickets                                                   | List all service tickets                        |
| GET    | /service_tickets/&lt;int:service_ticket_id&gt;                     | Get a service ticket                            |
| GET    | /service_tickets/most-tickets                                      | Get the mechanics with the most service tickets |
| PUT    | /service_tickets/&lt;int:service_ticket_id&gt;/update-part         | Update a service ticket parts                   |
| PUT    | /service_tickets/&lt;int:service_ticket_id&gt;/update-mechanics    | Update a service ticket mechanics               |
| PUT    | /service_tickets/&lt;int:service_ticket_id&gt;/service-ticket-info | Update a service ticket's information           |
| DELETE | /service_tickets/&lt;int:service_ticket_id&gt;                     | Delete a service ticket                         |

### Inventories

| Method | Endpoint                              | Description              |
| ------ | ------------------------------------- | ------------------------ |
| POST   | /inventories                          | Create an inventory part |
| GET    | /inventories                          | List all inventory parts |
| GET    | /inventories/&lt;int:inventory_id&gt; | Get an inventory part    |
| PUT    | /inventories/&lt;int:inventory_id&gt; | Update an inventory part |
| DELETE | /inventories/&lt;int:inventory_id&gt; | Delete an inventory part |

```

```

## Swagger UI

This project includes Swagger documentation to easily explore and test the API.

Once the app is running, visit:
http://127.0.0.1:5000/api/docs/

## Unit Testing

Unit tests are included for all major functionality using Python’s unittest framework.

Activate your virtual environment:

    source .venv/bin/activate # Mac/Linux
    venv\Scripts\activate # Windows

Run all tests in the app/tests folder:

    python -m unittest discover -s app/tests

Test results will show pass/fail status for each endpoint and function.

### What is Tested

CRUD operations for customers, mechanics, inventories, and service tickets.

Role-based access restrictions.

Service ticket assignments and part usage.

Edge cases like invalid IDs and forbidden actions.

## Swagger CLI and Nodemon

This project uses swagger-cli and nodemon to manage and automatically rebuild the Swagger API documentation.

    @apidevtools/swagger-cli – Used to bundle multiple Swagger YAML files into a single merged specification.

    nodemon – Watches files for changes and automatically executes a command when changes are detected.

To run:

    npm run watch-swagger

Whenever you update any Swagger YAML file, the merged specification will automatically regenerate in swagger_build/merged.yaml. You can then view it in Swagger UI.
