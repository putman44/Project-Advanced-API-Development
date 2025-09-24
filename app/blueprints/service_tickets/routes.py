from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, ServiceTicket, Customer, db
from . import service_tickets_bp


@service_tickets_bp.route("/", methods=["POST"])
def create_service_ticket():
    # Example request JSON:
    # {
    #     "customer_id": "1",
    #     "VIN": "1HGCM82633A123456",
    #     "service_date": "2023-10-01",
    #     "service_desc": "Oil change and tire rotation",
    #     "mechanic_ids": [1, 2]
    # }
    try:

        ticket_data = service_ticket_schema.load(request.json)

        mechanic_ids = ticket_data.pop("mechanic_ids", [])
        new_ticket = ServiceTicket(**ticket_data)

        # Handle mechanics if provided
        if mechanic_ids:
            new_ticket.mechanics = (
                db.session.query(Mechanic).filter(Mechanic.id.in_(mechanic_ids)).all()
            )

        db.session.add(new_ticket)
        db.session.commit()
        return service_ticket_schema.jsonify(new_ticket), 201
    except ValidationError as e:
        return (
            jsonify(e.messages),
            400,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@service_tickets_bp.route("/", methods=["GET"])
def get_service_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(tickets)


@service_tickets_bp.route("/<int:ticket_id>", methods=["GET"])
def get_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

    if ticket:
        return service_ticket_schema.jsonify(ticket), 200
    return jsonify({"error": "Service ticket not found."}), 404


@service_tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
def update_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    try:
        data = service_ticket_schema.load(request.json, partial=True)

        mechanic_ids = data.pop("mechanic_ids", None)
        if mechanic_ids is not None:
            mechanics = (
                db.session.query(Mechanic).filter(Mechanic.id.in_(mechanic_ids)).all()
            )
            if len(mechanics) != len(mechanic_ids):
                return jsonify({"error": "One or more mechanic IDs are invalid"}), 400
            ticket.mechanics = mechanics

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
def delete_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    db.session.delete(ticket)
    db.session.commit()
    return (
        jsonify({"message": f"Service ticket {ticket_id} deleted successfully."}),
        200,
    )
