from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, db
from . import mechanics_bp


@mechanics_bp.route("/", methods=["POST"])
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
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics)


@mechanics_bp.route("/<int:mechanic_id>", methods=["GET"])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Mechanic not found."}), 404


@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
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
