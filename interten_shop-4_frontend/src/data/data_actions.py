import os

import requests
from dotenv import load_dotenv
from flask import session


load_dotenv()
PRODS_URL = os.getenv("PRODS_URL")
USERS_URL = os.getenv("USERS_URL")
TOKENS_URL = os.getenv("TOKENS_URL")


def get_product(prod_id: str, url: str = PRODS_URL) -> dict:
    product = requests.get(url + prod_id).json()
    if product:
        return product[0]


def get_products(url: str = PRODS_URL) -> dict:
    return requests.get(url).json()


def del_product(prod_id: str, url: str = PRODS_URL) -> dict:
    return requests.delete(url + prod_id).json()


def add_product(name: str, description: str, img_url: str, price: float, url: str = PRODS_URL) -> dict:
    body = dict(
        name=name,
        description=description,
        img_url=img_url,
        price=price
    )

    return requests.post(url, json=body).json()


def update_product(
    prod_id: str,
    name: str,
    description: str,
    img_url: str,
    price: float,
    url: str = PRODS_URL
    ) -> dict:

    body = dict(
        name=name,
        description=description,
        img_url=img_url,
        price=price
    )

    return requests.put(url + prod_id, json=body).json()


def signup(email: str, password: str, first_name: str|None = None, last_name: str|None = None, url: str = USERS_URL) -> dict:
    body = dict(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )

    return requests.post(url, json=body).json()


def get_tokens(email: str, password: str, url: str = TOKENS_URL) -> dict:
    body = dict(email=email, password=password)
    return requests.post(url, json=body).json()


def get_user(url: str = USERS_URL) -> dict:
    token = session.get("access_token")
    resp = requests.get(url, headers=dict(Authorization=f"Bearer {token}"))
    if resp.status_code == 200:
        return resp.json()
    else:
        return get_new_token()


def get_new_token(url: str = TOKENS_URL) -> dict:
    refresh_token = session.get("refresh_token")
    resp = requests.get(url, headers=dict(Authorization=f"Bearer {refresh_token}"))
    if resp.status_code == 200:
        session.update(resp.json())
        return get_user()


# def is_valid_token():
    