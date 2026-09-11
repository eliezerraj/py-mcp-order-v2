from pydantic import BaseModel, Field
from typing import Literal, Optional

class Product(BaseModel):
    sku: str = Field(
        description="Unique product SKU"
    )

class OrderItem(BaseModel):
    product: Product = Field(
        description="Product details for the order item"
    )
    quantity: int = Field(
        description="Quantity of the product in the order item"
    )
    discount: float = Field(
        description="Discount applied to the product in the order item"
    ) 

class OrderPayload(BaseModel):
    order_number: str = Field(
        description="Unique order number"
    )

    customer_id: str = Field(
        description="Unique customer ID associated with the order"
    )

    order_date: str = Field(
        description="Date when the order was placed"
    )

    order_item: list[OrderItem] = Field(
        description="List of items included in the order"
    )

