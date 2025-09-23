from marshmallow import pre_load, validates
from app.extensions import ma
from app.models import Mechanic
from app.functions import strip_input, validate_name, validate_email, validate_phone


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic

    @pre_load
    def preprocess(self, data, **kwargs):
        return strip_input(data)

    @validates("name")
    def check_name(self, value, **kwargs):
        return validate_name(value)

    @validates("email")
    def check_email(self, value, **kwargs):
        return validate_email(Mechanic, value)

    @validates("phone")
    def check_phone(self, value, **kwargs):
        return validate_phone(Mechanic, value)


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
