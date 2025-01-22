from datetime import datetime, UTC

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer, String, BigInteger, Float, DateTime, Boolean,
    ForeignKey
)

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    article = Column(BigInteger, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    sale_price = Column(Integer)
    sale = Column(Integer)
    rating = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    pics = Column(Integer, nullable=False)
    promo = Column(String)
    feedbacks = Column(Integer, nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    brand_id = Column(Integer, ForeignKey('brands.id'))
    tracking_id = Column(Integer, ForeignKey('tracked_products.id'))

    supplier = relationship('Supplier', back_populates='products')
    brand = relationship('Brand', back_populates='products')
    tracking = relationship('TrackedProduct', back_populates='product')


class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    rating = Column(Float, nullable=False)

    products = relationship('Product', back_populates='supplier')


class Brand(Base):
    __tablename__ = 'brands'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)

    products = relationship('Product', back_populates='brand')


class TrackedProduct(Base):
    __tablename__ = 'tracked_products'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    article_id = Column(Integer, unique=True, nullable=False)
    last_updated = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))
    is_active = Column(Boolean, nullable=False, default=True)

    product = relationship('Product', back_populates='tracking')
