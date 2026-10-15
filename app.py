from flask import Flask,request,render_template, redirect, send_file
from openpyxl import Workbook
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from database import get_connection


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("front_end.html")

@app.route("/products", methods=["GET"])
def get_products():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    connection.close()

    products_list = []
    for product in products:
        product_data = {
            "ProductID": product[0],
            "ProductName": product[1],
            "Brand": product[2],
            "Category": product[3],
            "Quality": product[4],
            "Price": product[5],
            "Quantity": product[6]
        }
        products_list.append(product_data)
    return render_template("products.html",products=products_list)


@app.route("/products", methods=["POST"])
def add_products():
    name = request.form.get("ProductName")
    brand = request.form.get("Brand")
    category = request.form.get("Category")
    quality = request.form.get("Quality")
    price = request.form.get("Price")
    quantity = request.form.get("Quantity")

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

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ProductID FROM products WHERE ProductName = %s", (name,))
    existing_product = cursor.fetchone()

    if existing_product:
        cursor.close()
        connection.close()
        return render_template("add_product.html", message="Product already exists"), 409

    cursor.execute("INSERT INTO products (ProductName, Brand, Category, Quality, Price, Quantity) VALUES (%s, %s, %s,%s, %s, %s)", (name, brand, category, quality, price, quantity))
    connection.commit()
    cursor.close()
    connection.close()
    return render_template("add_product.html", message="Product added successfully"), 201

@app.route("/update_product", methods=["POST"])
def update_product_form():
    product_id = request.form.get("product_id")
    name = request.form.get("name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")


    if not product_id or not name or not price or not quantity:
        return render_template("update.html", message="ProductID, ProductName, price and Quantity are required"), 400
    
    try:
        product_id = int(product_id)
        price = float(price)
        quantity = int(quantity)
    except ValueError:
            return render_template("update.html", message="Invalid number format for product id, price, or quantity"), 400
    
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ProductID FROM products WHERE ProductID = %s", (product_id,))
    if cursor.fetchone() is None:
        cursor.close()
        connection.close()
        return render_template("update.html", message="Product not found"), 404

    cursor.execute("UPDATE products SET ProductName = %s, Price = %s, Quantity = %s WHERE ProductID = %s", 
                   (name, price, quantity, product_id))
    connection.commit()
    cursor.close()
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

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ProductID FROM products WHERE ProductID = %s", (product_id,))
    if cursor.fetchone() is None:
        connection.close()
        return render_template("delete_product.html", message="Product not found"), 404

    cursor.execute("DELETE FROM products WHERE ProductID = %s", (product_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return render_template("delete_product.html", message="Product deleted successfully")

@app.route("/sales", methods=["POST"])
def sell_product():
    name = request.form.get("ProductName")
    quantity_sold = request.form.get("Quantity")

    if not name or not quantity_sold:
        return render_template("sales.html", message="Product name and quantity sold are required"), 400

    try:
        quantity_sold = int(quantity_sold)
    except ValueError:
        return render_template("sales.html", message="Quantity must be an integer"), 400

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT ProductID, Price, Quantity FROM products WHERE ProductName = %s", (name,))
    product = cursor.fetchone()

    if product is None:
        connection=get_connection()
        cursor = connection.cursor()
        return render_template("sales.html", message="Product not found"), 404

    product_id, price, current_quantity = product

    if quantity_sold > current_quantity:
        cursor.close()
        connection.close()
        return render_template("sales.html", message="Not enough stock"), 400

    new_quantity = current_quantity - quantity_sold
    total_price = price * quantity_sold

    cursor.execute("UPDATE products SET quantity = %s WHERE ProductID = %s", (new_quantity, product_id))
    cursor.execute("INSERT INTO sales (ProductID, Quantity, total_price) VALUES (%s, %s, %s)",
                   (product_id, quantity_sold, total_price))

    connection.commit()
    cursor.close()
    connection.close()

    return render_template("sales.html", message="Product sold successfully",
                           product=name,
                           quantity_sold=quantity_sold,
                           total_price=total_price), 201

@app.route("/stock_value", methods=["GET"])
def calculate_stock_value():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT Price, Quantity FROM products")
    products = cursor.fetchall()
    cursor.close()
    connection.close()

    total_value = 0
    for product in products:
        price = product[0]
        quantity = product[1]
        total_value += price * quantity
    return render_template("Total_Value.html",total_value=total_value)

@app.route("/low_stock", methods=["GET"])
def low_stock():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products WHERE quantity <= 5")
    products = cursor.fetchall()
    connection.close()

    if not products:
        return render_template("low_stock.html", message="No product found")

    products_list = []
    for product in products:
        product_data = {"ProductID": product[0], "ProductName": product[1],"Brand": product[2],"Category": product[3],"Quality": product[4], "Price": product[5], "Quantity": product[6]}
        products_list.append(product_data)
    return render_template("low_stock.html", products=products_list)

@app.route("/search_product", methods=["GET"])
def get_product():
    name = request.args.get("ProductName","").strip()

    if not name:
      return render_template("search.html", message="Please enter a product name"),400
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products WHERE LOWER(ProductName) LIKE LOWER(%s)",('%'+ name +'%',))
    product = cursor.fetchone()
    connection.close()

    if product is None:
        return render_template("search.html", message="Product not found"), 404

    product_data = {"ProductID": product[0], "ProductName": product[1],"Brand": product[2],"Category": product[3],"Quality": product[4], "Price": product[5], "Quantity": product[6]}
    return render_template("search.html",product_data=product_data)

@app.route("/download_excel", methods=["GET"])
def download_excel():
    
    wb = Workbook()
    ws = wb.active

    
    ws.append(["ProductID", "ProductName","Brand", "Category", "Quality", "Price", "Quantity"])

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
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
    c = canvas.Canvas(output, pagesize=landscape(letter))
    width, height = landscape(letter)

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    connection.close()
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, height - 30, "ID")
    c.drawString(100, height - 30, "Name")
    c.drawString(300, height - 30, "Brand")
    c.drawString(400, height - 30, "Category")
    c.drawString(500, height - 30, "Quality")
    c.drawString(600, height - 30, "Price")
    c.drawString(700, height - 30, "Quantity")

    y = height - 60
    for product in products:
        if y < 50:
           c.showPage()
           y = height - 60
        c.setFont("Helvetica", 10)
        c.drawString(30, y, str(product[0]))
        c.drawString(100, y,str(product[1]))
        c.drawString(300, y,str(product[2]))
        c.drawString(400, y,str(product[3]))
        c.drawString(500, y,str(product[4]))
        c.drawString(600, y,str(product[5]))
        c.drawString(700, y,str(product[6]))
        y -= 20

    c.save()
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="Inventory.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)

