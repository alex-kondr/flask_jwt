import os

import requests
from dotenv import load_dotenv


load_dotenv()
PRODS_URL = os.getenv("PRODS_URL")


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
