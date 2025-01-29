import os
import binascii
from datetime import timedelta
from enum import Enum, auto

from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import create_access_token, get_current_user, jwt_required, JWTManager, get_jwt_identity

from src.database.models import db
from src.data import parse_data
from src.database import db_actions


load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_URI")
app.config["JWT_SECRET_KEY"] = binascii.hexlify(os.urandom(24))
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
db.init_app(app)
api = Api(app)
jwt = JWTManager(app)


# with app.app_context():
#     db.create_all()
#     parse_data.get_products()


class TypeHTTPRequest(Enum):
    user = auto()
    token = auto()


class ProductAPI(Resource):
    def row_db_to_json(self, products: list):
        data = []
        for product in products:
            data.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "img_url": product.img_url,
                "price": product.price
            })

        data_json = jsonify(data)
        data_json.status_code = 201
        return data_json

    def get(self, product_id: str|None = None):
        if product_id:
            product = db_actions.get_product(product_id)
            return self.row_db_to_json([product])
        else:
            products = db_actions.get_products()
            return self.row_db_to_json(products)

    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument("name")
        parse.add_argument("description")
        parse.add_argument("img_url")
        parse.add_argument("price")
        args = parse.parse_args()
        prod_id = db_actions.add_product(
            name=args.get("name"),
            description=args.get("description"),
            img_url=args.get("img_url"),
            price=args.get("price")
        )
        response = jsonify(dict(product_id=prod_id))
        response.status_code = 201
        return response

    def put(self, product_id: str):
        parse = reqparse.RequestParser()
        parse.add_argument("name")
        parse.add_argument("description")
        parse.add_argument("price")
        parse.add_argument("img_url")
        args = parse.parse_args()
        msg = db_actions.edit_product(
            prod_id=product_id,
            name=args.get("name"),
            description=args.get("description"),
            img_url=args.get("img_url"),
            price=args.get("price")
        )
        response = jsonify(msg)
        response.status_code = 201
        return response

    def delete(self, product_id: str):
        msg = db_actions.del_product(product_id)
        response = jsonify(msg)
        response.status_code = 201
        return response


class UserAPI(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        print(f"{current_user = }")
        resp = jsonify(dict(logged_in_as=current_user))
        resp.status_code = 200
        return resp



    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("first_name")
        parser.add_argument("last_name")
        parser.add_argument("email")
        parser.add_argument("password")
        args = parser.parse_args()
        db_actions.add_user(
            first_name=args.get("first_name"),
            last_name=args.get("last_name"),
            email=args.get("email"),
            password=args.get("password")
        )
        resp = jsonify("Додано")
        resp.status_code = 201
        return resp


class TokenAPI(Resource):


    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email")
        parser.add_argument("password")
        args = parser.parse_args()
        tokens = db_actions.get_tokens(email=args.get("email"), password=args.get("password"))
        response = jsonify(tokens)
        response.status_code = 200
        return response


api.add_resource(ProductAPI, "/api/products/", "/api/products/<product_id>/")
api.add_resource(UserAPI, "/api/users/", "/api/users/<user_id>/")
api.add_resource(TokenAPI, "/api/tokens/")


if __name__ == "__main__":
    app.run(debug=True, port=3000)
