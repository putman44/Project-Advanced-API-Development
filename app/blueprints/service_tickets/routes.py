# app/blueprints/service_tickets/routes.py
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import (
    Inventory,
    InventoryServiceTicket,
    Mechanic,
    ServiceTicket,
    db,
)
from . import service_tickets_bp
from .schemas import (
    service_ticket_schema,
    service_tickets_schema,
    edit_service_ticket_mechanics_schema,
    edit_service_ticket_info_schema,
)
from app.blueprints.mechanics.schemas import mechanics_schema
from app.utils.utils import token_required, roles_required
from app.blueprints.inventories.schemas import (
    inventory_service_ticket_schema,
)


@service_tickets_bp.route("/", methods=["POST"])
@token_required
@roles_required(["mechanic"])
def create_service_ticket(user, user_role):
    """
    Create a service ticket.
    Example request JSON:
    {
        "customer_id": 1,
        "VIN": "1HGCM82633A123456",
        "service_date": "2025-12-12",
        "service_desc": "Oil change",
        "mechanic_ids": [1, 2]
    }
    """
    try:
        ticket_data = service_ticket_schema.load(request.json)

        mechanic_ids = ticket_data.pop("mechanic_ids", [])
        new_ticket = ServiceTicket(**ticket_data)

        mechanics = (
            db.session.query(Mechanic).filter(Mechanic.id.in_(mechanic_ids)).all()
        )

        new_ticket.mechanics = mechanics

        db.session.add(new_ticket)
        db.session.commit()
        return service_ticket_schema.jsonify(new_ticket), 201

    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@service_tickets_bp.route("/", methods=["GET"])
@token_required
def get_service_tickets(user, user_role):
    tickets = db.session.execute(select(ServiceTicket)).scalars().all()

    if len(tickets) < 1:
        return jsonify({"message": "There are no service ticket in the system."})
    return service_tickets_schema.jsonify(tickets)


@service_tickets_bp.route("/<int:ticket_id>", methods=["GET"])
@token_required
def get_service_ticket(user, user_role, ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route("/most-tickets", methods=["GET"])
def get_mechanic_with_most_service_tickets():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(
        key=lambda mechanic: len(mechanic.service_tickets), reverse=True
    )  # params:expression

    return mechanics_schema.jsonify(mechanics), 200


@service_tickets_bp.route("/<int:ticket_id>/update-parts", methods=["PUT"])
@token_required
@roles_required(["mechanic"])
def update_service_ticket_part(user, user_role, ticket_id):
    try:
        # Load request data with schema
        ticket_parts_data = inventory_service_ticket_schema.load(request.json)

        service_ticket = db.session.get(ServiceTicket, ticket_id)
        if not service_ticket:
            return jsonify({"error": "Service ticket not found"}), 404

        part = db.session.get(Inventory, ticket_parts_data["inventory_id"])
        if not part:
            return (
                jsonify(
                    {
                        "error": f"Part id {ticket_parts_data['inventory_id']} does not exist"
                    }
                ),
                400,
            )

        quantity_used = ticket_parts_data.get("quantity_used", 0)
        quantity_returned = ticket_parts_data.get("quantity_returned", 0)

        # Find existing inventory link for this ticket
        inventory_link = next(
            (
                link
                for link in service_ticket.inventory_links
                if link.inventory_id == part.id
            ),
            None,
        )

        if not inventory_link:
            inventory_link = InventoryServiceTicket(
                service_ticket_id=ticket_id,
                inventory_id=part.id,
                quantity_used=0,
            )
            db.session.add(inventory_link)

        # Handle adding parts
        if quantity_used > 0:
            if part.quantity < quantity_used:
                return (
                    jsonify({"error": f"Not enough {part.part_name}s in inventory"}),
                    400,
                )
            inventory_link.quantity_used += quantity_used
            part.quantity -= quantity_used

        # Handle removing parts
        if quantity_returned > 0:
            if inventory_link.quantity_used < quantity_returned:
                return (
                    jsonify(
                        {
                            "error": f"Cannot return more {part.part_name}s than used in this ticket"
                        }
                    ),
                    400,
                )
            inventory_link.quantity_used -= quantity_returned
            part.quantity += quantity_returned

        db.session.commit()

        messages = []
        if quantity_used > 0:
            messages.append(f"{quantity_used} {part.part_name}(s) added")
        if quantity_returned > 0:
            messages.append(f"{quantity_returned} {part.part_name}(s) removed")

        return (
            jsonify(
                {"message": " and ".join(messages), "ticket_id": service_ticket.id}
            ),
            200,
        )

    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@service_tickets_bp.route("/<int:ticket_id>/update-mechanics", methods=["PUT"])
@token_required
@roles_required(["mechanic"])
def update_service_ticket_mechanics(user, user_role, ticket_id):
    try:
        data = edit_service_ticket_mechanics_schema.load(request.json)

        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({"error": "Service ticket not found"}), 404

        for mechanic_id in data.get("add_mechanic_ids", []):
            mechanic = db.session.get(Mechanic, mechanic_id)

            if mechanic and mechanic not in ticket.mechanics:
                ticket.mechanics.append(mechanic)

        for mechanic_id in data.get("remove_mechanic_ids", []):
            mechanic = db.session.get(Mechanic, mechanic_id)
            if mechanic and mechanic in ticket.mechanics:
                if len(ticket.mechanics) <= 1:
                    return (
                        jsonify(
                            {
                                "error": "Cannot remove the last mechanic from service ticket; at least one must remain."
                            }
                        ),
                        400,
                    )
                ticket.mechanics.remove(mechanic)

        # Handle mechanics
        # mechanic_ids = data.pop("mechanic_ids", None)
        # if mechanic_ids is not None:
        #     mechanics = (
        #         db.session.query(Mechanic)
        #         .filter(Mechanic.id.in_(mechanic_ids))
        #         .all()
        #         # SELECT * FROM mechanics WHERE id IN (mechanic_ids)
        #     )
        #     if len(mechanics) != len(mechanic_ids):
        #         return jsonify({"error": "One or more mechanic IDs are invalid"}), 400

        #     # Optional: prevent removing the last mechanic
        #     if len(mechanics) == 0 and len(ticket.mechanics) <= 1:
        #         return (
        #             jsonify({"error": "Cannot remove the last mechanic from a ticket"}),
        #             400,
        #         )

        #     ticket.mechanics = mechanics

        db.session.commit()
        return service_ticket_schema.jsonify(ticket), 200

    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@service_tickets_bp.route("/<int:ticket_id>/update-info", methods=["PUT"])
@token_required
@roles_required(["mechanic"])
def update_service_ticket_info(user, user_role, ticket_id):
    try:
        data = edit_service_ticket_info_schema.load(request.json, partial=True)

        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({"error": "Service ticket not found"}), 404

        for key, value in data.items():
            setattr(ticket, key, value)

        db.session.commit()
        return service_ticket_schema.jsonify(ticket), 200

    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@service_tickets_bp.route("/<int:ticket_id>", methods=["DELETE"])
@token_required
@roles_required(["mechanic"])
def delete_service_ticket(user, user_role, ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    db.session.delete(ticket)
    db.session.commit()
    return (
        jsonify({"message": f"Service ticket {ticket_id} deleted successfully."}),
        200,
    )
