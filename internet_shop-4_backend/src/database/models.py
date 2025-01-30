from typing import List
from datetime import datetime
from dataclasses import dataclass, field

from sqlalchemy import String, Table, Column, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import get_jwt_identity, create_access_token, create_refresh_token, decode_token


Base = declarative_base()
db = SQLAlchemy(model_class=Base, engine_options=dict(echo=True))


rev_prod_assoc = Table(
    "rev_prod_assoc",
    Base.metadata,
    Column("review_id", ForeignKey("reviews.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)


user_shopping_cart_assoc = Table(
    "user_shopping_cart_assoc",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)


user_shop_list_assoc = Table(
    "user_shop_list_assoc",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("shop_list_id", ForeignKey("shop_list.id"), primary_key=True)
)


shop_list_prod_assoc = Table(
    "shop_list_prod_assoc",
    Base.metadata,
    Column("shop_list_id", ForeignKey("shop_list.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)


@dataclass
class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    text: Mapped[str] = mapped_column(String())


@dataclass
class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    name: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(String())
    img_url: Mapped[str] = mapped_column(String())
    price: Mapped[float] = mapped_column()
    reviews: Mapped[List[Review]] = relationship(secondary=rev_prod_assoc)


@dataclass
class ShopList(Base):
    __tablename__ = "shop_list"

    id: Mapped[str] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    products: Mapped[List[Product]] = relationship(secondary=shop_list_prod_assoc)


@dataclass
class User(Base):
    __tablename__ = "users"
    password_1: Mapped[str] = field(repr=False, default=mapped_column(String()))

    id: Mapped[str] = mapped_column(String(), primary_key=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(), unique=True)
    __password: Mapped[str] = mapped_column(String(), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False)
    shopping_cart: Mapped[List[Product]] = relationship(secondary=user_shopping_cart_assoc)
    shop_list: Mapped[List[ShopList]] = relationship(secondary=user_shop_list_assoc)

    @property
    def password(self):
        return "Don`t use this"

    @password.setter
    def password(self, pwd: str):
        self.__password = generate_password_hash(pwd)

    def get_tokens(self, password) -> dict[str, str] | dict[None, None]:
        if check_password_hash(self.__password, password):
            return dict(
                access_token=create_access_token(identity=self.id),
                refresh_token=create_refresh_token(identity=self.id)
            )
        return dict(
                access_token=None,
                refresh_token=None
        )
