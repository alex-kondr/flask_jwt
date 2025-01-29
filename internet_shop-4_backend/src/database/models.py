from typing import List
from datetime import datetime

from sqlalchemy import String, Table, Column, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, relationship
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


user_prod_assoc = Table(
    "user_prod_assoc",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)


user_shop_list_assoc = Table(
    "user_shop_list_assoc",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    text: Mapped[str] = mapped_column(String())


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    name: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(String())
    img_url: Mapped[str] = mapped_column(String())
    price: Mapped[float] = mapped_column()
    reviews: Mapped[List[Review]] = relationship(secondary=rev_prod_assoc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(), primary_key=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(), unique=True)
    __password: Mapped[str] = mapped_column(String(), nullable=False)
    access_token: Mapped[str] = mapped_column(String(), nullable=True, default=None)
    refresh_token: Mapped[str] = mapped_column(String(), nullable=True, default=None)
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False)
    products: Mapped[List[Product]] = relationship(secondary=user_prod_assoc)
    shop_list: Mapped[List[Product]] = relationship(secondary=user_shop_list_assoc)

    @property
    def password(self):
        return "Don`t use this"

    @password.setter
    def password(self, pwd: str):
        self.__password = generate_password_hash(pwd)

    def get_tokens(self, password) -> dict[str, str] | dict[None, None]:
        if check_password_hash(self.__password, password):
            self.access_token = create_access_token(identity=self.email)
            self.refresh_token = create_refresh_token(identity=self.email)
            return dict(
                access_token=create_access_token(identity=self.email),
                refresh_token=create_refresh_token(identity=self.email)
            )
        return dict(
                access_token=None,
                refresh_token=None
        )

    # def is_verified_token(self, access_token):
    #     try:
            

    # def get_refresh_token(self, refresh_token):
        

