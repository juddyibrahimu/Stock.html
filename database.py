import mysql.connector

    
def get_connection ():
  connection = mysql.connector.connect(
   host = "localhost",
   user = "root",
   password = "judith@2004",
   database = "inventory"
  )
  return connection
print("Database created successfully!")
