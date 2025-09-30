from marshmallow import pre_load, validates
from app.extensions import ma
from app.models import Mechanic
from app.functions import (
    strip_input,
    validate_name,
    validate_email,
    validate_password,
    validate_phone,
)

# from app.blueprints.service_tickets.schemas import ServiceTicketSchema


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic

    # service_tickets = ma.Nested("ServiceTicketSchema", many=True, dump_only=True)

    @pre_load
    def preprocess(self, data, **kwargs):
        return strip_input(data)

    @validates("name")
    def check_name(self, value, **kwargs):
        return validate_name(value)

    @validates("password")
    def check_password(self, value, **kwargs):
        return validate_password(value)

    @validates("email")
    def check_email(self, value, **kwargs):
        ctx = getattr(self, "context", {}) or {}
        if not ctx.get("login", False):
            return validate_email(Mechanic, value)
        return value

    @validates("phone")
    def check_phone(self, value, **kwargs):
        return validate_phone(Mechanic, value)


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
login_schema = MechanicSchema(exclude=["name", "phone", "salary"])
login_schema.context = {"login": True}
