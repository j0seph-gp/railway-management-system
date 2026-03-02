import mysql.connector as sql
from mysql.connector import Error

# ------------------------------------------------------------
# Function to establish connection and create database/table
# ------------------------------------------------------------
def setup_database():
    try:
        # Connect to MySQL
        con = sql.connect(host="localhost", user="root", password="joseph@12345678")
        cur = con.cursor()
        # Create database if not exists
        cur.execute("CREATE DATABASE IF NOT EXISTS railway_db")
        cur.execute("USE railway_db")

        # Create table if not exists
        cur.execute("""
        CREATE TABLE IF NOT EXISTS trains(
            train_no INT PRIMARY KEY,
            train_name VARCHAR(50),
            source VARCHAR(50),
            destination VARCHAR(50),
            total_seats INT,
            available_seats INT
        )
        """)
        con.commit()
        print("Database and table are ready.\n")
    except Error as e:
        print("Error while setting up database:", e)
    finally:
        if con.is_connected():
            cur.close()
            con.close()

# ------------------------------------------------------------
# Function to connect to database
# ------------------------------------------------------------
def connect_db():
    try:
        con = sql.connect(
            host="localhost",
            user="root",
            password="joseph@12345678",
            database="railway_db"
        )
        return con   # ✅ Return connection

    except Error as e:
        print("Database connection failed:", e)
        return None

# ------------------------------------------------------------
# Function to add train details
# ------------------------------------------------------------
def add_train():
    try:
        con = connect_db()
        if con is None:
            return
        cur = con.cursor()
        train_no = int(input("Enter Train Number: "))
        train_name = input("Enter Train Name: ")
        source = input("Enter Source Station: ")
        destination = input("Enter Destination Station: ")
        total_seats = int(input("Enter Total Seats: "))
        available_seats = int(input("Enter Available Seats: "))

        query = "INSERT INTO trains VALUES (%s, %s, %s, %s, %s, %s)"
        data = (train_no, train_name, source, destination, total_seats, available_seats)
        cur.execute(query, data)
        con.commit()
        print("Train added successfully!\n")
    except Error as e:
        print("Error while adding train:", e)
    except ValueError:
        print("Invalid input! Please enter correct data types.")
    finally:
        if con and con.is_connected():
            cur.close()
            con.close()

# ------------------------------------------------------------
# Function to view all train records
# ------------------------------------------------------------
def view_trains():
    try:
        con = connect_db()
        if con is None:
            return
        cur = con.cursor()
        cur.execute("SELECT * FROM trains")
        records = cur.fetchall()
        if len(records) == 0:
            print("No records found.\n")
        else:
            print("Train Records:")
            print("-" * 80)
            print(f"{'Train No.':<10} {'Train Name':<20} {'Source':<15} {'Destination':<15} {'Total':<8} {'Available':<10}")
            print("-" * 80)
            for row in records:
                print(f"{row[0]:<10} {row[1]:<20} {row[2]:<15} {row[3]:<15} {row[4]:<8} {row[5]:<10}")
            print()
    except Error as e:
        print("Error while fetching records:", e)
    finally:
        if con and con.is_connected():
            cur.close()
            con.close()

# ------------------------------------------------------------
# Function to search a train by number
# ------------------------------------------------------------
def search_train():
    try:
        con = connect_db()
        if con is None:
            return
        cur = con.cursor()
        train_no = int(input("Enter Train Number to Search: "))
        cur.execute("SELECT * FROM trains WHERE train_no=%s", (train_no,))
        record = cur.fetchone()
        if record:
            print("\nTrain Found:")
            print(f"Train Number: {record[0]}")
            print(f"Train Name: {record[1]}")
            print(f"Source: {record[2]}")
            print(f"Destination: {record[3]}")
            print(f"Total Seats: {record[4]}")
            print(f"Available Seats: {record[5]}\n")
        else:
            print("Train not found.\n")
    except Error as e:
        print("Error while searching:", e)
    except ValueError:
        print("Invalid input. Please enter a valid train number.")
    finally:
        if con and con.is_connected():
            cur.close()
            con.close()

# ------------------------------------------------------------
# Function to update train details
# ------------------------------------------------------------
def update_train():
    try:
        con = connect_db()
        if con is None:
            return
        cur = con.cursor()
        train_no = int(input("Enter Train Number to Update: "))
        cur.execute("SELECT * FROM trains WHERE train_no=%s", (train_no,))
        if cur.fetchone():
            print("Enter new details (leave blank to skip):")
            new_name = input("New Train Name: ")
            new_source = input("New Source: ")
            new_dest = input("New Destination: ")
            new_total = input("New Total Seats: ")
            new_avail = input("New Available Seats: ")

            update_query = "UPDATE trains SET "
            updates = []
            data = []

            if new_name:
                updates.append("train_name=%s")
                data.append(new_name)
            if new_source:
                updates.append("source=%s")
                data.append(new_source)
            if new_dest:
                updates.append("destination=%s")
                data.append(new_dest)
            if new_total:
                updates.append("total_seats=%s")
                data.append(int(new_total))
            if new_avail:
                updates.append("available_seats=%s")
                data.append(int(new_avail))

            if updates:
                update_query += ", ".join(updates) + " WHERE train_no=%s"
                data.append(train_no)
                cur.execute(update_query, tuple(data))
                con.commit()
                print("Train details updated successfully!\n")
            else:
                print("No updates made.\n")
        else:
            print("Train not found.\n")
    except Error as e:
        print("Error while updating record:", e)
    except ValueError:
        print("Invalid input! Please enter correct data types.")
    finally:
        if con and con.is_connected():
            cur.close()
            con.close()

# ------------------------------------------------------------
# Function to delete train record
# ------------------------------------------------------------
def delete_train():
    try:
        con = connect_db()
        if con is None:
            return
        cur = con.cursor()
        train_no = int(input("Enter Train Number to Delete: "))
        cur.execute("DELETE FROM trains WHERE train_no=%s", (train_no,))
        con.commit()
        if cur.rowcount > 0:
            print("Train record deleted successfully.\n")
        else:
            print("Train not found.\n")
    except Error as e:
        print("Error while deleting record:", e)
    except ValueError:
        print("Invalid input. Please enter a valid train number.")
    finally:
        if con and con.is_connected():
            cur.close()
            con.close()

# ------------------------------------------------------------
# Main Menu
# ------------------------------------------------------------
def main_menu():
    while True:
        print("==== RAILWAY MANAGEMENT SYSTEM ====")
        print("1. Add Train Record")
        print("2. View All Trains")
        print("3. Search Train")
        print("4. Update Train Details")
        print("5. Delete Train Record")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            add_train()
        elif choice == '2':
            view_trains()
        elif choice == '3':
            search_train()
        elif choice == '4':
            update_train()
        elif choice == '5':
            delete_train()
        elif choice == '6':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n")

# ------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------
if __name__ == "__main__":
    setup_database()
    main_menu()
