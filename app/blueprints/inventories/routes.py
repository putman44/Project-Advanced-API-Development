from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from app.models import db, Inventory
from .schemas import InventorySchema, inventory_schema, inventories_schema
from . import inventories_bp
from app.utils.utils import encode_token, token_required, roles_required


@inventories_bp.route("/", methods=["POST"])
@token_required
@roles_required("mechanic")
def create_part(user, user_role):
    try:
        part_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400

    part = Inventory(**part_data)
    db.session.add(part)
    db.session.commit()

    return inventory_schema.jsonify(part), 201


@inventories_bp.route("/", methods=["GET"])
def get_parts():
    parts = db.session.query(Inventory).all()
    return inventories_schema.jsonify(parts), 200


@inventories_bp.route("/<int:part_id>", methods=["GET"])
def get_part(part_id):
    part = db.session.get(Inventory, part_id)

    if not part:
        return jsonify({"message": "Invalid part id"}), 404
    return inventory_schema.jsonify(part), 200


@inventories_bp.route("/<int:part_id>", methods=["PUT"])
@token_required
@roles_required("mechanic")
def update_part(user, user_role, part_id):
    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"message": "Invalid part id"}), 404

    # Attach current part_id to schema for uniqueness check
    inventory_schema._current_part_id = part_id

    try:
        # partial=True allows updating only some fields
        part_data = inventory_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400

    # Apply updates dynamically
    for key, value in part_data.items():
        setattr(part, key, value)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    return inventory_schema.jsonify(part), 200


@inventories_bp.route("/<int:part_id>", methods=["DELETE"])
@token_required
@roles_required("mechanic")
def delete_part(user, user_role, part_id):
    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"message": "Invalid part id"}), 404

    db.session.delete(part)
    db.session.commit()

    return (
        jsonify(
            {"message": f"Successfully deleted part id {part_id}: {part.part_name}"}
        ),
        200,
    )
