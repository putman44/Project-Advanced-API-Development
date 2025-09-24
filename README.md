# Mechanic Service API

A RESTful API for managing customers, mechanics, and service tickets built with Flask, SQLAlchemy, and MySQL.

---

## Table of Contents

1. [Features](#features)  
2. [Tech Stack](#tech-stack)  
3. [Installation](#installation)  
4. [Entity-Relationship-Diagram](#entity-relationship-diagram)  
5. [Database Models](#database-models)  
6. [API Endpoints](#api-endpoints)  

---

## Features

- CRUD operations for customers, mechanics, and service_tickets.  
- One-to-many relationships (Customer → ServiceTicket).  
- Many-to-many relationships with extra data (ServiceTicket ↔ Mechanic via ServiceTicketMechanic).  
- Marshmallow schemas for serialization and validation.  
---

## Tech Stack

- **Backend:** Python, Flask  
- **Database:** MySQL  
- **ORM:** SQLAlchemy  
- **Serialization:** Flask-Marshmallow, Marshmallow-SQLAlchemy  

---

## Installation

```bash
git clone https://github.com/putman44/Assignment-Building-API-with-Application-Factory-Pattern
cd Assignment-Building-API-with-Application-Factory-Pattern

python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

pip install Flask Flask-SQLAlchemy Flask-Marshmallow mysql-connector-python marshmallow-sqlalchemy
```

## Entity-Relationship-Diagram

![Entity Relationship Diagram](Mechanic_Erd.png)

## API Endpoints


### Customers

| Method | Endpoint              | Description         |
|--------|-----------------------|---------------------|
| POST   | /customers            | Create a customer   |
| GET    | /customers            | List all customers  |
| GET    | /customers/&lt;int:customer_id&gt;       | Get a customer      |
| PUT    | /customers/&lt;int:customer_id&gt;       | Update a customer   |
| DELETE | /customers/&lt;int:customer_id&gt;       | Delete a customer   |

### Mechanics

| Method | Endpoint         | Description         |
|--------|------------------|---------------------|
| POST   | /mechanics       | Create a mechanic   |
| GET    | /mechanics       | List all mechanics  |
| GET    | /mechanics/&lt;int:mechanic_id&gt;  | Get a mechanic      |
| PUT    | /mechanics/&lt;int:mechanic_id&gt;  | Update a mechanic   |
| DELETE | /mechanics/&lt;int:mechanic_id&gt;  | Delete a mechanic   |

### Service Tickets

| Method | Endpoint                | Description             |
|--------|-------------------------|-------------------------|
| POST   | /service_tickets        | Create a service ticket |
| GET    | /service_tickets        | List all service tickets|
| GET    | /service_tickets/&lt;int:service_ticket_id&gt;   | Get a service ticket    |
| PUT    | /service_tickets/&lt;int:service_ticket_id&gt;   | Update a service ticket |
| DELETE | /service_tickets/&lt;int:service_ticket_id&gt;   | Delete a service ticket |
