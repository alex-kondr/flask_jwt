from flask import Flask, render_template, redirect, url_for

from src.data import data_actions


app = Flask(__name__, template_folder="src/templates")


@app.get("/")
def index():
    products = data_actions.get_products()
    return render_template("index.html", products=products)


@app.get("/product/<id>/")
def get_product(id):
    product = data_actions.get_product(id)
    return render_template("product.html", product=product)


@app.get("/buy_product/<id>/")
def buy_product(id):
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
