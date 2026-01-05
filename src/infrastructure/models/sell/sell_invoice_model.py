from sqlalchemy import Column, ForeignKey, Integer, String, DateTime,Float
from infrastructure.databases.base import Base
class SellInvoiceModel(Base):
    __tablename__ = 'sell_invoices'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('sell_customers.id'))
    invoice_date = Column(DateTime)
    total_amount = Column(Float)
    status = Column(String(50))
    invoice_code = Column(String(12), unique=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    blank_amount = Column(Float)
    paid_amount = Column(Float)
    # customer = relationship("CustomerModel", back_populates="invoices")
    # items = relationship("SellInvoiceItemModel", back_populates="invoice")
    # payments = relationship("PayTranModel", back_populates="invoice")
    
class SellInvoiceItemModel(Base):
    __tablename__ = 'sell_invoice_items'

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('sell_invoices.id'))
    product_id = Column(Integer, ForeignKey('sell_products.id'))
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_price = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    # invoice = relationship("SellInvoiceModel", back_populates="items")