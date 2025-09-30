from .schemas import mechanic_schema, mechanics_schema, login_schema
from app.blueprints.service_tickets.schemas import service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, db, ServiceTicket
from . import mechanics_bp
from app.extensions import limiter, cache
from app.utils.utils import encode_token, token_required, roles_required


@mechanics_bp.route("/login", methods=["POST"])
def login():
    try:
        mechanic_credentials = login_schema.load(request.json)
        email = mechanic_credentials["email"]
        password = mechanic_credentials["password"]
    except ValidationError as e:
        return jsonify(e.messages)

    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic and mechanic.password == password:
        auth_token = encode_token(
            mechanic.user_uuid,
            mechanic.role,
            mechanic.token_version,
        )
        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token,
        }
        return jsonify(response), 200
    else:
        return jsonify({"messages": "Invalid email or password"}), 401


@mechanics_bp.route("/", methods=["POST"])
@limiter.limit("5 per day")
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
        new_mechanic = Mechanic(**mechanic_data)
        db.session.add(new_mechanic)
        db.session.commit()
        return mechanic_schema.jsonify(new_mechanic), 201
    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@mechanics_bp.route("/", methods=["GET"])
@limiter.limit("100 per minute")
# @cache.cached(timeout=300)
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics)


@mechanics_bp.route("/<int:mechanic_id>", methods=["GET"])
@limiter.limit("100 per minute")
@cache.cached(timeout=300)
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Mechanic not found."}), 404


@mechanics_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_mechanics_my_tickets(user, user_role):

    service_tickets = user.service_tickets

    return service_tickets_schema.jsonify(service_tickets), 200


@mechanics_bp.route("/", methods=["PUT"])
@limiter.limit("20 per hour")
@token_required
@roles_required("mechanic")
def update_mechanic(user, user_role):

    data = mechanic_schema.load(request.json, partial=True)
    for key, value in data.items():
        setattr(user, key, value)
    db.session.commit()
    return mechanic_schema.jsonify(user), 200


@mechanics_bp.route("/", methods=["DELETE"])
@limiter.limit("20 per hour")
@token_required
@roles_required(["mechanic"])
def delete_mechanic(user, user_role):

    # Check each service ticket assigned to this mechanic
    for ticket in user.service_tickets:
        if len(ticket.mechanics) <= 1:
            return (
                jsonify(
                    {
                        "error": f"Cannot delete mechanic id:{user.id} {user.name}. "
                        f"Service ticket {ticket.id} would have no mechanics assigned."
                    }
                ),
                400,
            )

    # Safe to delete
    db.session.delete(user)
    db.session.commit()
    return (
        jsonify({"message": f"Mechanic id: {user.id} deleted successfully."}),
        200,
    )
