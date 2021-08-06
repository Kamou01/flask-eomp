import hmac
import sqlite3

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity


class userInfo(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('online_store.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(userInfo(data[0], data[3], data[4]))
    return new_data


def init_usertable():
    conn = sqlite3.connect('online_store.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")

    conn.commit()
    print("user table created successfully.")


init_usertable()
users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return username_table.get(user_id, None)


def products_table():
    with sqlite3.connect('online_store.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "type TEXT NOT NULL)")
        print("product table create successfully.")


init_usertable()
products_table()

users = fetch_users()


app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = 'super-secret'

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']

        print(first_name, username, password, last_name)

        with sqlite3.connect('online_store.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password) VALUES(?, ?, ?, ?)", (first_name, last_name, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201

    return response


@app.route('/addingProduct/', methods=["POST"])
def adding_product():
    response = {}

    if request.method == "POST":
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        type = request.form['type']

        with sqlite3.connect('online_store.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products("
                               "name,"
                               "price,"
                               "description,"
                               "type) VALUES(?, ?, ?, ?)", (name, price, description, type))
                conn.commit()
                response["status_code"] = 201
                response['description'] = "Product added successfully"
        return response


@app.route('/delete/<int:id>/')
def delete_products(product_id):
    response = {}

    with sqlite3.connect('online_store.db') as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM products WHERE id=" + str(product_id))
        connection.commit()
        response['status code'] = 200
        response['message'] = "Product deleted."
    return response


@app.route('/view_products/')
def view_products():
    response = {}

    with sqlite3.connect('online_store.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products')
        conn.commit()

        products = cursor.fetchall()
        response["status_code"] = 201
        response["products"] = products
        response['description'] = "Here are the products"

    return response


@app.route('/updating_product/', methods=["PUT"])
def update_product(id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('online_store.db') as conn:
            print(request.json)
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("name") is not None:
                put_data["name"] = incoming_data.get("name")

                with sqlite3.connect('online_store.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE products SET name =? WHERE id", (put_data["name"], id))

                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

    return response


@app.route('/view_product/<int:id>')
def view_product(id):
    response = {}

    with sqlite3.connect('online_store.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id =? ', str(id))
        product = cursor.fetchone()
        conn.commit()

        response['status code'] = 201
        response['description'] = "Here are the products"
        response['data'] = product

    return response


if __name__ == '__main__':
    app.run()
