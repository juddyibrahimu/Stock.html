from flask import Flask,request,render_template, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify("front_end.html")

@app.route("/products", methods=["GET"])
def get_products():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    connection.close()

    products_list = []
    for product in products:
        product_data = {
            "id": product[0],
            "name": product[1],
            "price": product[2],
            "quantity": product[3]
        }
        products_list.append(product_data)
    return render_template("products.html",products=products_list)

@app.route("/search", methods=["GET"])
def search_product():
    query = request.args.get("name", "").strip()
    if not query:
        return render_template({"message": "Search term is required"}), 400

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, price, quantity FROM products WHERE name LIKE ?", (f"%{query}%",))
    products = cursor.fetchall()
    connection.close()

    results = [{"id": p[0], "name": p[1], "price": p[2], "quantity": p[3]} for p in products]
    return jsonify(results)

@app.route("/products", methods=["POST"])
def add_products():
    name = request.form.get("name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")

    if not name or not price or not quantity:
        return jsonify({"message": "Name, price and quantity are required"}), 400

<<<<<<< HEAD
    try:
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        return jsonify({"message": "Invalid price or quantity"}), 400
=======
    if not name:
        return render_template("add_product.html",message="Name is not found"),400
    if not  name or not price or  not quantity:
        return render_template("add_product.html",message="Name, price and quantity are required"),400

    price = float(price)
    quantity = int(quantity)
>>>>>>> aa21f5c (Stock)

    if price < 0:
        return render_template("add_product.html",message="Price cannot be negative"), 400
    if quantity < 0:
<<<<<<< HEAD
        return jsonify({"message": "Quantity cant be negative"}), 400
=======
        return render_template("add_product.html",message="Quantity cant be negative"), 400
    
>>>>>>> aa21f5c (Stock)

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM products WHERE name = ?", (name,))
    existing_product = cursor.fetchone()

    if existing_product:
        connection.close()
<<<<<<< HEAD
        return jsonify({"message": "Product already exists"}), 409

    cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (name, price, quantity))
=======
        return render_template("add_product.html",message="Product already exists"), 409
    cursor.execute("""INSERT INTO products(name,price,quantity) VALUES (?,?,?)""", (name, price, quantity))
    
>>>>>>> aa21f5c (Stock)
    connection.commit()
    connection.close()
    return render_template("add_product.hml", message= "Product added successfully"), 201

@app.route("/update_product", methods=["POST"])
<<<<<<< HEAD
def update_product_form():
=======
def update_product():
>>>>>>> aa21f5c (Stock)
    product_id = request.form.get("product_id")
    name = request.form.get("name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")
<<<<<<< HEAD

    if not product_id or not name or not price or not quantity:
        return jsonify({"message": "Product id, name, price and quantity are required"}), 400

    try:
        product_id = int(product_id)
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        return jsonify({"message": "Invalid number format for product id, price, or quantity"}), 400
=======
>>>>>>> aa21f5c (Stock)

    if not product_id or not name or not price or not quantity:
            return render_template("update.html",messag="Product id, name, price and quantity are required"), 400
    
    try:
        product_id = int(product_id)
        price = float(price)
        quantity = int(quantity)
    except ValueError:
            return render_template("update.html", message="Invalid number format for product id, price, or quantity"), 400
    
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
<<<<<<< HEAD
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if cursor.fetchone() is None:
        connection.close()
        return jsonify({"message": "Product not found"}), 404

=======
    cursor.execute("""UPDATE products SET name = ?, price = ?,quantity = ? WHERE id = ?""", 
                  (name, price,quantity, product_id))
    if cursor.fetchone is None:
         connection.close()
         return render_template("update.html", message="Product not found"), 404
    
>>>>>>> aa21f5c (Stock)
    cursor.execute("UPDATE products SET name = ?, price = ?, quantity = ? WHERE id = ?", 
                   (name, price, quantity, product_id))
    connection.commit()
    connection.close()
<<<<<<< HEAD
    return jsonify({"message": "Product updated successfully"})

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product_api(product_id):
    data = request.get_json() or {}
    name = data.get("name")
    price = data.get("price")
    quantity = data.get("quantity")

    if not name or price is None or quantity is None:
        return jsonify({"message": "Name, price and quantity are required"}), 400

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if cursor.fetchone() is None:
        connection.close()
        return jsonify({"message": "Product not found"}), 404

    cursor.execute("UPDATE products SET name = ?, price = ?, quantity = ? WHERE id = ?", 
                   (name, float(price), int(quantity), product_id))
    connection.commit()
    connection.close()
    return jsonify({"message": "Product updated successfully"})

@app.route("/delete_product", methods=["POST"])
def delete_product_form():
    product_id = request.form.get("product_id")
    if not product_id:
        return jsonify({"message": "Product ID is required"}), 400

    try:
        product_id = int(product_id)
    except ValueError:
        return jsonify({"message": "Invalid product ID"}), 400

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if cursor.fetchone() is None:
        connection.close()
        return jsonify({"message": "Product not found"}), 404

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    connection.commit()
    connection.close()
    return jsonify({"message": "Product deleted successfully"})
=======
    return render_template("update.html", message="Product updated")
>>>>>>> aa21f5c (Stock)

@app.route("/sales", methods=["POST"])
def sell_product():
    name = request.form.get("name")
    quantity_sold = request.form.get("quantity")

    if not name or not quantity_sold:
        return jsonify({"message": "Product name and quantity sold are required"}), 400

    try:
        quantity_sold = int(quantity_sold)
    except ValueError:
        return jsonify({"message": "Quantity must be an integer"}), 400

    connection = sqlite3.connect("inventory.db", timeout=10)
    cursor = connection.cursor()

    cursor.execute("SELECT id, price, quantity FROM products WHERE name = ?", (name,))
    product = cursor.fetchone()

    if product is None:
        connection.close()
        return render_template("sales.html", message="Product not found"), 404

    product_id, price, current_quantity = product

    if quantity_sold > current_quantity:
        connection.close()
<<<<<<< HEAD
        return jsonify({"message": "Not enough stock"}), 400

=======
        return render_template("sales.html", message="Not enough stock"), 400
>>>>>>> aa21f5c (Stock)
    new_quantity = current_quantity - quantity_sold
    total_price = price * quantity_sold

    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))
    cursor.execute("INSERT INTO sales (product_id, quantity, total_price) VALUES (?, ?, ?)",
                   (product_id, quantity_sold, total_price))

    connection.commit()
    connection.close()

<<<<<<< HEAD
    return jsonify({"message": "Product sold successfully",
                    "product": name,
                    "quantity_sold": quantity_sold,
                    "total_price": total_price}), 201
=======
    return render_template("sales.html", message="Product sold successfully",
                    product=name,
                    quantity_sold=quantity_sold,
                    total_price=total_price),201
>>>>>>> aa21f5c (Stock)

@app.route("/stock_value", methods=["GET"])
def calculate_stock_value():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT price, quantity FROM products")
    products = cursor.fetchall()
    connection.close()

    total_value = 0
    for product in products:
        price = product[0]
        quantity = product[1]
        total_value += price * quantity
    return render_template("Total_Value.html",total_value=total_value)

@app.route("/low_stock", methods=["GET"])
def low_stock():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
<<<<<<< HEAD
    cursor.execute("SELECT id, name, price, quantity FROM products WHERE quantity <= 5")
=======

    cursor.execute("""SELECT id,name,price,quantity FROM products WHERE quantity <= 10""")

>>>>>>> aa21f5c (Stock)
    products = cursor.fetchall()
    connection.close()

    if not products:
        return jsonify({"message": "No product found"})

    products_list = []
    for product in products:
        product_data = {"id": product[0], "name": product[1], "price": product[2], "quantity": product[3]}
        products_list.append(product_data)
<<<<<<< HEAD
    return jsonify(products_list)
=======
    return render_template("low_stock.html", products=products_list)
    

>>>>>>> aa21f5c (Stock)

@app.route("/show_product", methods=["GET"])
def get_product():
    name = request.args.get("name")
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
<<<<<<< HEAD
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
=======

    cursor.execute("SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?)",('%'+ name +'%',))
>>>>>>> aa21f5c (Stock)
    product = cursor.fetchone()
    connection.close()

    if product is None:
<<<<<<< HEAD
        return jsonify({"message": "Product not found"}), 404

=======
        return render_template("search.html",message="Product's name not found"), 404
>>>>>>> aa21f5c (Stock)
    product_data = {"id": product[0], "name": product[1], "price": product[2], "quantity": product[3]}
    return render_template("search.html",product_data=product_data)

<<<<<<< HEAD
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
=======

@app.route("/delete_product", methods=["POST"])
def delete_product_form():
    product_id = request.form.get("product_id")
    if not product_id:
            return jsonify("delete.html", message="Product ID is required"), 400
    
    try:
            product_id = int(product_id)
    except ValueError:
            return render_template("delete.html", message="Invalid product ID"), 400
    
>>>>>>> aa21f5c (Stock)
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if product is None:
        connection.close()
<<<<<<< HEAD
        return jsonify({"message": "Product not found"}), 404
=======
        return render_template("delete.html", message="Product not found"), 404

    cursor.execute("DELETE FROM products WHERE id = ?",(product_id,))
>>>>>>> aa21f5c (Stock)

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    connection.commit()
    connection.close()
<<<<<<< HEAD
    return jsonify({"message": "Product deleted successfully"})
=======

    return render_template("delete.html", message="Product deleted successfully")
>>>>>>> aa21f5c (Stock)

if __name__ == "__main__":
    app.run(debug=True)
