from marshmallow import pre_load, validates
from app.extensions import ma
from app.models import Customer
from app.functions import strip_input, validate_name, validate_email, validate_phone


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer

    @pre_load
    def preprocess(self, data, **kwargs):
        return strip_input(data)

    @validates("name")
    def check_name(self, value, **kwargs):
        return validate_name(value)

    @validates("email")
    def check_email(self, value, **kwargs):
        return validate_email(Customer, value)

    @validates("phone")
    def check_phone(self, value, **kwargs):
        return validate_phone(Customer, value)


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


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
