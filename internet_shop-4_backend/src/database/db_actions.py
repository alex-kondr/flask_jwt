from uuid import uuid4
from typing import List

from src.database.models import db, Product, Review, User


def get_products() -> List[Product]:
    # return db.get_or_404(db.session.query(Product))
    return db.session.query(Product).all()


def get_product(prod_id: str) -> Product:
    return db.one_or_404(db.session.query(Product).where(Product.id == prod_id))
    # return db.session.query(Product).where(Product.id == prod_id).first()


def add_product(
    name: str,
    description: str,
    img_url: str,
    price: float
) -> str:
    product = Product(
        id=uuid4().hex,
        name=name,
        description=description,
        img_url=img_url,
        price=price
    )
    db.session.add(product)
    db.session.commit()
    return product.id


def edit_product(
    prod_id: str,
    name: str,
    description: str,
    img_url: str,
    price: float
) -> str:
    product = db.one_or_404(db.session.query(Product).where(Product.id == prod_id))
    product.name = name
    product.description = description
    product.img_url = img_url
    product.price = price
    db.session.commit()
    return "Successful"


def del_product(prod_id: str) -> str:
    product = db.one_or_404(db.session.query(Product).where(Product.id == prod_id))
    db.session.delete(product)
    db.session.commit()
    return "Successful"


def add_review_by_product(review: Review, prod_id: str) -> str:
    product = db.one_or_404(db.session.query(Product).where(Product.id == prod_id))
    product.reviews.append(review)
    db.session.commit()
    return "Successful"


def add_review(text: str) -> str:
    review = Review(id=uuid4().hex, text=text)
    db.session.add(review)
    db.session.commit()
    return "Successful"


def add_user(first_name, last_name, email, password):
    user = User(
        id=uuid4().hex,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password
    )
    db.session.add(user)
    db.session.commit()


def get_tokens(email:str, password: str) -> tuple[str, str]:
    user = db.one_or_404(db.session.query(User).where(User.email==email))
    tokens = user.get_tokens(password)
    db.session.commit()
    return tokens
