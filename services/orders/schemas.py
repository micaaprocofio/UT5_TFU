from pydantic import BaseModel
from datetime import datetime

class OrderBase(BaseModel):
    customer_id: int
    total: float

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    date: datetime
    
    class Config:
        from_attributes = True