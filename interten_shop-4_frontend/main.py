import os
import binascii

from flask import Flask, render_template, redirect, url_for, session, request

from src.data import data_actions


app = Flask(__name__, template_folder="src/templates")
app.secret_key = binascii.hexlify(os.urandom(24))


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


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        tokens = data_actions.get_tokens(**request.form)
        session.update(tokens)
        return redirect(url_for("cabinet"))
    return render_template("login.html")


@app.get("/cabinet/")
def cabinet():
    data = data_actions.get_user()
    print(f"{data = }")
    if data:
        return data
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
