from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="user")
    balance = Column(DECIMAL(15, 2), default=0.0)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text)


class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.user_id"))
    title = Column(String)
    description = Column(Text)
    year_created = Column(Integer)
    is_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class SystemLog(Base):
    __tablename__ = "system_logs"

    log_id = Column(Integer, primary_key=True)
    level = Column(String)
    source = Column(String)
    message = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Auction(Base):
    __tablename__ = "auctions"

    auction_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), unique=True)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    start_price = Column(DECIMAL(12, 2))
    current_price = Column(DECIMAL(12, 2), default=0)
    status = Column(String, default='planned') # planned, active, finished

class Bid(Base):
    __tablename__ = "bids"

    bid_id = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, ForeignKey("auctions.auction_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    amount = Column(DECIMAL(12, 2))
    bid_time = Column(TIMESTAMP, server_default=func.now())