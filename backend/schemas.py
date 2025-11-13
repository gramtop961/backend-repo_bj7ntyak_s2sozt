from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

# Each class corresponds to a MongoDB collection named after the lowercased class name

class Product(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str = Field(..., min_length=10, max_length=2000)
    price: float = Field(..., ge=0)
    image: str = Field(..., description="URL to product image")
    type: Literal['mug', 'bowl', 'plate', 'vase']
    in_stock: bool = True

class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    message: str = Field(..., min_length=5, max_length=3000)

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(1, ge=1, le=10)
