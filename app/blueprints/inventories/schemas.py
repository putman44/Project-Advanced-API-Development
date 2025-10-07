from marshmallow import ValidationError, pre_load, validates, validates_schema
from app.extensions import ma
from app.models import InventoryServiceTicket, Inventory, db
from app.functions import (
    strip_input,
    validate_name,
)


class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory

    @pre_load
    def preprocess(self, data, **kwargs):
        return strip_input(data)

    @validates("part_name")
    def validate_part_name(self, value):
        # Access the current part_id if set by the route
        part_id = getattr(self, "_current_part_id", None)

        # Check uniqueness
        existing = (
            db.session.query(Inventory).filter(Inventory.part_name == value).first()
        )
        if existing and existing.id != part_id:
            raise ValidationError("Part name already exists")

        return validate_name(value)

    @validates("price")
    def validate_price(self, value, **kwargs):
        if value is None or value < 0.01:
            raise ValidationError("Price must be at least 0.01")
        return value

    @validates("quantity")
    def validate_quantity(self, value, **kwargs):
        if value < 1:
            raise ValidationError("Quantity must be at least 1")


class InventoryServiceTicketSchema(ma.SQLAlchemySchema):
    inventory_id = ma.Int(required=True)
    quantity_used = ma.Int(required=False, default=0)
    quantity_returned = ma.Int(required=False, default=0)

    class Meta:
        model = InventoryServiceTicket
        include_relationships = True
        fields = (
            "inventory_id",
            "quantity_used",
            "quantity_returned",
        )

    @validates_schema
    def validate_quantities(self, data, **kwargs):
        used = data.get("quantity_used", 0)
        returned = data.get("quantity_returned", 0)

        if used < 0:
            raise ValidationError("quantity_used cannot be negative")
        if returned < 0:
            raise ValidationError("quantity_returned cannot be negative")
        if used == 0 and returned == 0:
            raise ValidationError(
                "At least one of quantity_used or quantity_returned must be provided"
            )


inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)

inventory_service_ticket_schema = InventoryServiceTicketSchema()
inventories_service_ticket_schema = InventoryServiceTicketSchema(many=True)
