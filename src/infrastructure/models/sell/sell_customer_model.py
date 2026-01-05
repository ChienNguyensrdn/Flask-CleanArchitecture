from sqlalchemy import Column, ForeignKey, Integer, String, DateTime,Float
from infrastructure.databases.base import Base
class SellCustomerModel(Base):
    __tablename__ = 'sell_customers'

    id = Column(Integer, primary_key=True)
    customer_name = Column(String(100))
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    address = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)