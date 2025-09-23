import re
from marshmallow import ValidationError, pre_load, validates
from app.extensions import ma
from app.models import Customer
from app.models import db

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_REGEX = re.compile(r"^\d{3}-\d{3}-\d{4}$")

session = db.session


def strip_strings(data):
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = value.strip()
    return data


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        # load_instance = True

    # With load_instance = True:
    # customer_data = customer_schema.load({
    #     "name": "Taylor",
    #     "email": "test@example.com",
    #     "phone": "123-456-7890"
    # })

    # print(type(customer_data))
    # # <class 'app.models.Customer'>

    # print(customer_data.email)
    # # test@example.com

    # customer_data is a Customer object, ready to add to your DB with db.session.add(customer_data).

    # With load_instance = False (default):
    # customer_data = customer_schema.load({
    #     "name": "Taylor",
    #     "email": "test@example.com",
    #     "phone": "123-456-7890"
    # })

    # print(type(customer_data))
    # # <class 'dict'>

    # print(customer_data["email"])
    # # test@example.com

    @pre_load
    def strip_input(self, data, **kwargs):
        return strip_strings(data)

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value:
            raise ValidationError("Name cannot be blank")
        if len(value) < 2:
            raise ValidationError("Name must be at least 2 characters long")
        return value

    @validates("email")
    def validate_email(self, value, **kwargs):
        if not EMAIL_REGEX.match(value):
            raise ValidationError(
                "Invalid email address, must be in the format 'example@domain.com'"
            )
        return value

    @validates("phone")
    def validate_phone(self, value, **kwargs):
        if not value:
            raise ValidationError("Phone number cannot be blank")
        if not PHONE_REGEX.match(value):
            raise ValidationError(
                "Invalid phone number. Must be 5-15 digits and can start with +"
            )
        return value


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
