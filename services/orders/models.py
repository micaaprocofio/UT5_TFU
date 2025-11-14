from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from database import Base

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True) 
    date = Column(DateTime, default=datetime.utcnow)
    total = Column(Float)