from marshmallow import ValidationError, pre_load, validates
from app.extensions import ma
from app.models import ServiceTicket, Customer, Mechanic, db
from datetime import date
from app.functions import strip_input
import re
from app.blueprints.inventories.schemas import inventories_service_ticket_schema

VIN_REGEX = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")  # Excludes I, O, Q


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket

    ticket_id = ma.Int(load_only=True)
    customer_id = ma.Int(required=True)
    mechanic_ids = ma.List(ma.Int(), required=True)

    inventory_links = ma.Nested(
        inventories_service_ticket_schema, exclude=["service_ticket", "inventory"]
    )

    mechanics = ma.Nested(
        "MechanicSchema",
        many=True,
        dump_only=True,
        exclude=[
            "email",
            "phone",
            "salary",
            "token_version",
            "role",
            "password",
            "user_uuid",
        ],
    )

    @pre_load
    def preprocess(self, data, **kwargs):
        return strip_input(data)

    @validates("mechanic_ids")
    def validate_mechanic_ids(self, value, **kwargs):
        if not value or len(value) == 0:
            raise ValidationError("At least one mechanic must be assigned")

        mechanics = db.session.query(Mechanic).filter(Mechanic.id.in_(value)).all()
        if len(mechanics) != len(value):
            raise ValidationError("One or more mechanic IDs are invalid")
        return value

    @validates("customer_id")
    def validate_customer_id(self, value, **kwargs):
        if not value:
            raise ValidationError("Customer ID cannot be blank")
        existing = db.session.query(Customer).filter(Customer.id == value).first()
        if not existing:
            raise ValidationError(f"Customer with ID {value} does not exist")
        return value

    @pre_load
    def preprocess(self, data, **kwargs):
        return strip_input(data)

    @validates("VIN")
    def validate_vin(self, value, **kwargs):
        if not value:
            raise ValidationError("VIN cannot be blank")
        if not VIN_REGEX.match(value.upper()):
            raise ValidationError(
                "Invalid VIN. Must be 17 characters (letters/digits, no I, O, Q)"
            )

    # Optional uniqueness check
    # existing = (
    #     db.session.query(ServiceTicket).filter(ServiceTicket.VIN == value).first()
    # )
    # if existing:
    #     raise ValidationError(f"VIN '{value}' is already registered")
    # return value
    @validates("service_date")
    def validate_service_date(self, value, **kwargs):
        if not value:
            raise ValidationError("Service date cannot be blank, must be YYYY-MM-DD")
        if value < date.today():
            raise ValidationError("Service date cannot be in the past")
        return value

    @validates("service_desc")
    def validate_service_desc(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Service description cannot be blank")
        if len(value.strip()) < 5:
            raise ValidationError(
                "Service description must be at least 5 characters long"
            )
        return value


class EditServiceTicketSchema(ServiceTicketSchema):
    add_mechanic_ids = ma.List(ma.Int(), required=True)
    remove_mechanic_ids = ma.List(ma.Int(), required=True)
    VIN = ma.Str()
    service_date = ma.Date()
    service_desc = ma.Str()

    class Meta:
        fields = (
            "add_mechanic_ids",
            "remove_mechanic_ids",
            "VIN",
            "service_date",
            "service_desc",
        )


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

edit_service_ticket_schema = EditServiceTicketSchema()
