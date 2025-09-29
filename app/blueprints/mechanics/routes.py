from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, db
from . import mechanics_bp
from app.extensions import limiter, cache


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
@cache.cached(timeout=300)
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


@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
@limiter.limit("20 per hour")
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    try:
        data = mechanic_schema.load(request.json, partial=True)
        for key, value in data.items():
            setattr(mechanic, key, value)
        db.session.commit()
        return mechanic_schema.jsonify(mechanic), 200
    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@mechanics_bp.route("/<int:mechanic_id>", methods=["DELETE"])
@limiter.limit("20 per hour")
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return (
        jsonify({"message": f"Mechanic id: {mechanic_id} deleted successfully."}),
        200,
    )
