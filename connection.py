import mysql.connector

print("Program started")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="joseph@12345678"
    )

    if conn.is_connected():
        print("Connected to MySQL successfully!")

except Exception as e:
    print("Connection failed!")
    print(e)

print("Program ended")