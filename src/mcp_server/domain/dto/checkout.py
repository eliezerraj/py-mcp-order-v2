from pydantic import BaseModel, Field
from typing import Literal, Optional

class Order(BaseModel):
    order_number: str = Field(
        description="Unique order number"
    )

class CreditCard(BaseModel):
    pan: str = Field(
        description="Credit card number used for the payment"
    )
    holder: str = Field(
        description="Name of the cardholder"
    )
    password: str = Field(
        description="Password of the credit card"
    )
    cvv: str = Field(
        description="CVV code of the credit card"
    )

class PaymentDetail(BaseModel):
    currency: str = Field(
        description="ISO 4217 Currency code",
        examples=["BRL"],
    )
    amount: float = Field(
        description="Payment amount",
        examples=[100.00],
    )
    credit_card: Optional[CreditCard] = Field(
        default=None,
        description="Credit card details when payment type uses card",
    )


class Payment(BaseModel):
    type: str = Field(
        description="Payment method used for the checkout"
    )
    payment_detail: list[PaymentDetail] = Field(
        description="Detailed information about the payment"
    )
    
class CheckoutPayload(BaseModel):
    order: Order = Field(
        description="Order details for the checkout"
    )
    
    payment: Payment = Field(
        description="Payment details for the checkout"
    )
