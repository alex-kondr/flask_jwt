import os
import binascii
from datetime import timedelta

from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from flask_migrate import Migrate

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
migrate = Migrate(app, db)


# with app.app_context():
#     db.create_all()
#     parse_data.get_products()


# @jwt.user_identity_loader
# def user_identity_lookup(user):
#     # input(f"{user = }")
#     return jsonify(user)


# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_header, jwt_data):
#     # input(f"{jwt_data = }")
#     identity = jwt_data["sub"]
#     return db_actions.get_user(identity)


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
        user_id = get_jwt_identity()
        # user_id = "d857654357364086995fc811f52163c2"
        user = db_actions.get_user(user_id)
        # print(f"{dict(user) = }")
        user.password = ""
        resp = jsonify(user)
        resp.status_code = 200
        return resp

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("first_name")
        parser.add_argument("last_name")
        parser.add_argument("email")
        parser.add_argument("password")
        args = parser.parse_args()
        db_actions.add_user(**args)
        resp = jsonify("Додано")
        resp.status_code = 201
        return resp


class TokenAPI(Resource):
    @jwt_required(refresh=True)
    def get(self):
        user_id = get_jwt_identity()
        return jsonify(access_token=create_access_token(identity=user_id))

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email")
        parser.add_argument("password")
        args = parser.parse_args()
        tokens = db_actions.get_tokens(**args)
        response = jsonify(tokens)
        response.status_code = 200
        return response


class ShopCart(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument("product_id")
        args = parser.parse_args()
        resp = jsonify(db_actions.add_prod_by_shop_cart(user_id=user_id, **args))
        resp.status_code = 201
        return resp


class ShopList(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        resp = jsonify(db_actions.add_shop_list_by_user(user_id=user_id))
        resp.status_code = 201
        return resp


api.add_resource(ProductAPI, "/api/products/", "/api/products/<product_id>/")
api.add_resource(UserAPI, "/api/users/", "/api/users/<user_id>/")
api.add_resource(TokenAPI, "/api/tokens/")
api.add_resource(ShopCart, "/api/add_product_by_shop_cart/")
api.add_resource(ShopList, "/api/add_shop_list/")


if __name__ == "__main__":
    app.run(debug=True, port=3000)
