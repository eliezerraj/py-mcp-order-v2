from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    id: Optional[int] = Field(
        default=None,
        description="Unique ID for the product"
    )
    
    sku: str = Field(
        default=None,
        description="Unique product SKU"
    )
    
    type: Optional[str] = Field(
        default=None,
        description="Type of the product"
    )
    
    name: Optional[str] = Field(
        default=None,
        description="Name of the product"
    )
    
    status: Optional[str] = Field(
        default=None,
        description="Status of the product"
    )

class OrderItem(BaseModel):
    product: Product = Field(
        description="Product details for the order item"
    )
    
    quantity: Optional[int] = Field(
        default=0,
        description="Quantity of the product in the order item"
    )
    
    discount: Optional[float] = Field(
        default=0,
        description="Discount applied to the product in the order item"
    ) 

    currency: Optional[str] = Field(
        default=None,
        description="Currency used for the order item"
    )
    
    amount: Optional[float] = Field(
        default=None,
        description="Total amount for the order item"
    )
    
    status: Optional[str] = Field(
        default=None,
        description="Status of the order item"
    )

class OrderPayload(BaseModel):
    order_number: Optional[str] = Field(
        default=None,
        description="Unique order number"
    )

    customer_id: str = Field(
        default=None,
        description="Unique customer ID associated with the order"
    )

    order_date: str = Field(
        default=None,
        description="Date when the order was placed"
    )

    order_item: list[OrderItem] = Field(
        default=None,
        description="List of items included in the order"
    )

class CreditCard(BaseModel):
    pan: str = Field(
        default=None,
        description="Credit card number used for the payment"
    )
    holder: str = Field(
        default=None,
        description="Name of the cardholder"
    )

class Payment(BaseModel):
    
    payment_date: str = Field(
        default=None,
        description="Date when the payment detail was recorded"
    )
    currency: str = Field(
        default=None,
        description="Currency used for the payment detail"
    )
    amount: float = Field(
        default=None,
        description="Amount for the payment detail"
    )

    type: Optional[str] = Field(
        default=None,
        description="Type of the payment"
    )    
    
    credit_card: Optional[CreditCard] = Field(
        default=None,
        description="Credit card details when payment type uses card",
    )
        
class PaymentDetails(BaseModel):
    payment_number: str = Field(
        default=None,
        description="Payment number",
    )
    transaction_id: str = Field(
        default=None,
        description="Transaction ID associated with the payment"
    )
    type: Optional[str] = Field(
        default=None,
        description="Type of the payment detail"
    )
    payment_detail: list[Payment] = Field(
        default=None,
        description="List of payment details associated with the order"
    )
            
class OrderResponse(BaseModel): 
    id: int = Field(
        default=None,
        description="Unique ID for the order response"
    )
    
    order_number: str = Field(
        description="Unique order number"
    )
    
    transaction_id: str = Field(
        default=None,
        description="Unique transaction ID associated with the order"
    )

    order_date: str = Field(
        default=None,
        description="Date when the order was placed"
    )
    
    status: str = Field(
        default=None,
        description="Status of the order"
    )
    
    currency: Optional[str] = Field(
        default=None,
        description="Currency used for the order"
    )
    
    amount: Optional[float] = Field(
        default=None,
        description="Total amount for the order"
    )

    customer_id: Optional[str] = Field(
        default=None,
        description="Unique customer ID associated with the order"
    )

    order_item: Optional[list[OrderItem]] = Field(
        default=None,
        description="List of items included in the order"
    )

    payment_details: Optional[list[PaymentDetails]] = Field(
        default=None,
        description="List of payment details associated with the order"
    )

class TimeSeriesData(BaseModel):
    date: str = Field(
        default=None,
        description="Date for the time series data point"
    )
    sum_quantity: int = Field(
        default=None,
        description="Sum of quantities for the time series data point"
    )
    sum_amount: float = Field(
        default=None,
        description="Sum of amounts for the time series data point"
    )

class TimeSeriesResponse(BaseModel):
    product: Optional[Product] = Field(
        default=None,
        description="Product associated with the time series"
    )
    
    time_series_data: Optional[list[TimeSeriesData]] = Field(
        default=None,
        description="List of time series data points for the product"
    )


#---------------------------------
# Checkout
#---------------------------------    
class PaymentCheckout(BaseModel):
    type: str = Field(
        default=None,
        description="Payment method used for the checkout"
    )
    
    payment_detail: list[Payment] = Field(
        default=None,
        description="Detailed information about the payment"
    )
        
class CheckoutPayload(BaseModel):
    order: OrderPayload = Field(
        default=None,
        description="Order details for the checkout"
    )
    
    payment: PaymentCheckout = Field(
        default=None,
        description="Payment details for the checkout"
    )

class CheckoutResponse(BaseModel):
    order: OrderResponse = Field(
        default=None,
        description="Order response for the checkout"
    )