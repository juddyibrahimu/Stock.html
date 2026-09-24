from flask import Flask,request,render_template, redirect, send_file
from openpyxl import Workbook
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("front_end.html")

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
    return render_template("search_results.html", results=results)

@app.route("/products", methods=["POST"])
def add_products():
    name = request.form.get("name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")

    if not name or not price or not quantity:
        return render_template("add_product.html", message="Name, price and quantity are required"), 400

    try:
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        return render_template("add_product.html", message="Invalid price or quantity"), 400

    if price < 0:
        return render_template("add_product.html",message="Price cannot be negative"), 400
    if quantity < 0:
        return render_template("add_product.html", message="Quantity cannot be negative"), 400

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM products WHERE name = ?", (name,))
    existing_product = cursor.fetchone()

    if existing_product:
        connection.close()
        return render_template("add_product.html", message="Product already exists"), 409

    cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (name, price, quantity))
    connection.commit()
    connection.close()
    return render_template("add_product.html", message="Product added successfully"), 201

@app.route("/update_product", methods=["POST"])
def update_product_form():
    product_id = request.form.get("product_id")
    name = request.form.get("name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")
    if not product_id or not name or not price or not quantity:
        return render_template("update.html", message="Product id, name, price and quantity are required"), 400

    try:
        product_id = int(product_id)
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        return render_template("update.html", message="Invalid number format for product id, price, or quantity"), 400
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
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if cursor.fetchone() is None:
        connection.close()
        return render_template("update.html", message="Product not found"), 404

    cursor.execute("UPDATE products SET name = ?, price = ?, quantity = ? WHERE id = ?", 
                   (name, price, quantity, product_id))
    connection.commit()
    connection.close()
    return render_template("update.html", message="Product updated successfully")

@app.route("/delete_product", methods=["POST"])
def delete_product_form():
    product_id = request.form.get("product_id")
    if not product_id:
        return render_template("delete_product.html", message="Product ID is required"), 400

    try:
        product_id = int(product_id)
    except ValueError:
        return render_template("delete_product.html", message="Invalid product ID"), 400

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if cursor.fetchone() is None:
        connection.close()
        return render_template("delete_product.html", message="Product not found"), 404

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    connection.commit()
    connection.close()
    return render_template("delete_product.html", message="Product deleted successfully")

@app.route("/sales", methods=["POST"])
def sell_product():
    name = request.form.get("name")
    quantity_sold = request.form.get("quantity")

    if not name or not quantity_sold:
        return render_template("sales.html", message="Product name and quantity sold are required"), 400

    try:
        quantity_sold = int(quantity_sold)
    except ValueError:
        return render_template("sales.html", message="Quantity must be an integer"), 400

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
        return render_template("sales.html", message="Not enough stock"), 400

    new_quantity = current_quantity - quantity_sold
    total_price = price * quantity_sold

    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))
    cursor.execute("INSERT INTO sales (product_id, quantity, total_price) VALUES (?, ?, ?)",
                   (product_id, quantity_sold, total_price))

    connection.commit()
    connection.close()

    return render_template("sales.html", message="Product sold successfully",
                           product=name,
                           quantity_sold=quantity_sold,
                           total_price=total_price), 201

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
    cursor.execute("SELECT id, name, price, quantity FROM products WHERE quantity <= 5")
    products = cursor.fetchall()
    connection.close()

    if not products:
        return render_template("low_stock.html", message="No product found")

    products_list = []
    for product in products:
        product_data = {"id": product[0], "name": product[1], "price": product[2], "quantity": product[3]}
        products_list.append(product_data)
    return render_template("low_stock.html", products=products_list)

@app.route("/show_product", methods=["GET"])
def get_product():
    name = request.args.get("name")
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?)",('%'+ name +'%',))
    product = cursor.fetchone()
    connection.close()

    if product is None:
        return render_template("search.html", message="Product not found"), 404

    product_data = {"id": product[0], "name": product[1], "price": product[2], "quantity": product[3]}
    return render_template("search.html",product_data=product_data)

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if product is None:
        connection.close()
        return render_template("delete_product.html", message="Product not found"), 404

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    connection.commit()
    connection.close()
    return render_template("delete_product.html", message="Product deleted successfully")

@app.route("/download_excel", methods=["GET"])
def download_excel():
    
    wb = Workbook()
    ws = wb.active

    
    ws.append(["ID", "Name", "Price", "Quantity"])

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, price, quantity FROM products")
    products = cursor.fetchall()
    connection.close()

    for product in products:
        ws.append(product)


    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="inventory.xlsx")
@app.route("/download_pdf", methods=["GET"])
def download_pdf():
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    width, height = letter

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, price, quantity FROM products")
    products = cursor.fetchall()
    connection.close()

    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, height - 30, "ID")
    c.drawString(100, height - 30, "Name")
    c.drawString(300, height - 30, "Price")
    c.drawString(400, height - 30, "Quantity")

    y = height - 50
    for product in products:
        c.setFont("Helvetica", 10)
        c.drawString(30, y, str(product[0]))
        c.drawString(100, y, product[1])
        c.drawString(300, y, str(product[2]))
        c.drawString(400, y, str(product[3]))
        y -= 20

    c.save()
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="inventory.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)

