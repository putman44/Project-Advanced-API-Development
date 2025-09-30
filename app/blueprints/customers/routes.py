from .schemas import customer_schema, customers_schema, login_schema
from app.blueprints.service_tickets.schemas import service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, ServiceTicket, db
from . import customers_bp
from app.utils.utils import encode_token, token_required


@customers_bp.route("/login", methods=["POST"])
def login():
    try:
        customer_credentials = login_schema.load(request.json)
        email = customer_credentials["email"]
        password = customer_credentials["password"]
    except ValidationError as e:
        return jsonify(e.messages)

    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()

    if customer and customer.password == password:
        auth_token = encode_token(
            customer.user_uuid,
            customer.role,
            customer.token_version,
        )

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token,
        }
        return jsonify(response), 200
    else:
        return jsonify({"messages": "Invalid email or password"}), 401


@customers_bp.route("/", methods=["POST"])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
        new_customer = Customer(**customer_data)
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@customers_bp.route("/", methods=["GET"])
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers)


@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404


@customers_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_my_tickets(user, user_role):
    service_tickets = user.service_tickets

    return service_tickets_schema.jsonify(service_tickets), 200


@customers_bp.route("/", methods=["PUT"])
@token_required
def update_customer(user, user_role):

    data = customer_schema.load(request.json, partial=True)
    for key, value in data.items():
        setattr(user, key, value)
    db.session.commit()
    return customer_schema.jsonify(user), 200


@customers_bp.route("/", methods=["DELETE"])
@token_required
def delete_customer(user, user_role):
    db.session.delete(user)
    db.session.commit()
    return (
        jsonify({"message": f"Customer id: {user.id}, successfully deleted."}),
        200,
    )
