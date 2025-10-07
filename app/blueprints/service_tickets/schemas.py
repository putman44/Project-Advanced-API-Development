from marshmallow import ValidationError, pre_load, validates
from app.extensions import ma
from app.models import ServiceTicket, Customer, Mechanic, db
from datetime import date, datetime
from app.functions import strip_input
import re
from app.blueprints.inventories.schemas import inventories_service_ticket_schema

VIN_REGEX = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")  # Excludes I, O, Q
DATE_REGEX = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")


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
        if not value or not value.strip():
            raise ValidationError("Service date cannot be blank, must be YYYY-MM-DD")

        if not DATE_REGEX.match(value):
            raise ValidationError("Service date must be in format YYYY-MM-DD")

        # Optional: check that the date is not in the past
        service_date_obj = datetime.strptime(value, "%Y-%m-%d").date()
        if service_date_obj < date.today():
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


class EditServiceTicketInfoSchema(ServiceTicketSchema):

    class Meta:
        fields = (
            "VIN",
            "service_date",
            "service_desc",
        )


class EditServiceTicketMechanicsSchema(ServiceTicketSchema):
    add_mechanic_ids = ma.List(ma.Int(), required=True)
    remove_mechanic_ids = ma.List(ma.Int(), required=True)

    class Meta:
        fields = (
            "add_mechanic_ids",
            "remove_mechanic_ids",
        )

    def _validate_mechanic_ids(self, value):

        mechanics = db.session.query(Mechanic).filter(Mechanic.id.in_(value)).all()
        if len(mechanics) != len(value):
            raise ValidationError("One or more mechanic IDs are invalid")
        return value

    @validates("add_mechanic_ids")
    def validate_add_mechanic_ids(self, value, **kwargs):
        return self._validate_mechanic_ids(value)

    @validates("remove_mechanic_ids")
    def validate_remove_mechanic_ids(self, value, **kwargs):
        return self._validate_mechanic_ids(value)


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

edit_service_ticket_info_schema = EditServiceTicketInfoSchema()
edit_service_ticket_mechanics_schema = EditServiceTicketMechanicsSchema()
