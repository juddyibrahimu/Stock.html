import sqlite3

    
connection = sqlite3.connect("inventory.db")
cursor = connection.cursor()


cursor.execute("""CREATE TABLE IF NOT EXISTS products ( 
id INTEGER PRIMARY KEY AUTOINCREMENT,  
name TEXT NOT NULL, 
price REAL NOT NULL,  
quantity INTEGER NOT NULL)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS sales(
id INTEGER PRIMARY KEY AUTOINCREMENT,
product_id INTEGER,
quantity INTEGER,
total_price REAL,
sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

connection.commit()
connection.close()
print("Database created successfully!")
