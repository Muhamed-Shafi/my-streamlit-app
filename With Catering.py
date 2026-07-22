import mysql.connector
from mysql.connector import Error
import random
def connect_db():
    try:
        conn = mysql.connector.connect(host='localhost',database='railway',user='root',password='123456')
        if conn.is_connected():
            print("Successfully connected to the MySQL database")
            return conn
        else:
            print("Failed to connect to the database")
            return None
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None
def create_database_and_tables(conn):
    cursor = conn.cursor()
    try:
        create_Train_table_query = """CREATE TABLE IF NOT EXISTS Train (Train_id INT AUTO_INCREMENT PRIMARY KEY,Train_name VARCHAR(100) NOT NULL,Source VARCHAR(100) NOT NULL,Destination VARCHAR(100) NOT NULL,Total_seats INT NOT NULL,Available_seats INT NOT NULL,Boarding_time DATETIME,Arrival_time DATETIME,AC_Seats int,Non_AC_Seats int);"""
        cursor.execute(create_Train_table_query)
        create_tickets_table_query = """CREATE TABLE IF NOT EXISTS Tickets (Pnr_number VARCHAR(10) PRIMARY KEY,Train_id INT NOT NULL,passenger_name VARCHAR(100) NOT NULL,passenger_age INT NOT NULL,Status VARCHAR(20) NOT NULL DEFAULT 'CONFIRMED',Booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(train_id) REFERENCES Train(train_id),Seat_type varchar(50));    		   """
        cursor.execute(create_tickets_table_query)
        conn.commit()
        print("Database tables ensured to exist (Train and Tickets).")
    except Error as e:
        conn.rollback()
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()
def display_Train(conn):
    cursor = conn.cursor()
    try:
        sql = "SELECT train_id, train_name, source, destination, available_seats,Boarding_time,Arrival_Time,AC_Seats,Non_AC_Seats FROM Train WHERE available_seats > 0"
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            print("\n")
            print(" "*54," Available Train's ")
            print("-"*144)
            print(f"{'ID':<9} | {'Name':<20} | {'Source':<15} | {'Destination':<15} | {'Seats':<5} |{'AC_Seats':<5}|{'Non-AC_Seats':<5}| {'Boarding':<20} | {'Arrival':<20}|")
            print("-" * 144)
            for row in results:
                boarding = row[5].strftime("%Y-%m-%d %H:%M") if row[5] else "N/A"
                arrival = row[6].strftime("%Y-%m-%d %H:%M") if row[6] else "N/A"
                print(f"{row[0]:<9} | {row[1]:<20} | {row[2]:<15} | {row[3]:<15} |  {row[4]:<5}| {row[7]:<6} | {row[8]:<10} | {boarding:<20} | {arrival:<20}|")
                print("-"*144)
        else:
            print("No Train available at the moment.")
    except Error as e:
        print(f"Error fetching Train: {e}")
    finally:
        cursor.close()
def book_ticket(conn, train_id, passenger_name, passenger_age,seat_type):
    cursor = conn.cursor()
    try:
        sql_check_seats = "SELECT available_seats FROM Train WHERE train_id = %s"
        cursor.execute(sql_check_seats, (train_id,))
        result = cursor.fetchone()
        if result and result[0] > 0:
            Available_seats = result[0]
            pnr_number = "PNR" + str(random.randint(100000, 999999))
            sql_insert_ticket = "INSERT INTO Tickets (pnr_number, train_id,passenger_name, passenger_age, status,seat_Type) VALUES (%s, %s, %s, %s, 'CONFIRMED',%s)"
            cursor.execute(sql_insert_ticket, (pnr_number, train_id, passenger_name, passenger_age,seat_type))
            cursor.execute("UPDATE Train SET available_seats = available_seats - 1 WHERE train_id = '%s'",(train_id,))
            if seat_type=='AC':
                cursor.execute("UPDATE Train SET ac_seats = ac_seats - 1 WHERE train_id = '%s'",(train_id,))
            elif seat_type=='Non-AC':
                cursor.execute("UPDATE Train SET Non_ac_seats = Non_ac_seats - 1 WHERE train_id = '%s'",(train_id,))
            conn.commit()
            print(f"Ticket booked successfully! Your PNR number is: {pnr_number}")
            return pnr_number
        elif result and result[0] == 0:
            print("Sorry, no seats are available on this train.")
            return None
        else:
            print("Error: Train not found.")
            return None
    except Error as e:
        conn.rollback() 
        print(f"Database error during booking: {e}")
        return None
    finally:
        cursor.close()
def check_ticket_status(conn, pnr_number):
    cursor = conn.cursor()
    try:
        sql = "SELECT T.pnr_number, T.passenger_name, T.passenger_age, T.status,T.seat_type, Tr.train_name, Tr.source, Tr.destination FROM Tickets AS T JOIN Train AS Tr ON T.train_id = Tr.train_id WHERE T.pnr_number = %s"
        cursor.execute(sql, (pnr_number,))
        result = cursor.fetchone()
        if result:
            pnr, name, age, status,seat_type, train_name, source, destination = result
            print("\n--- Ticket Details---")
            print(f"PNR Number: {pnr}")
            print(f"Status: {status}")
            print(f"Passenger: {name} (Age: {age})")
            print(f"Train Name: {train_name}")
            print(f"Your Seat type: {seat_type}")
            print(f"Route: {source} to {destination}")
            print("----------------------")
        else:
            print(f"Error: Ticket with PNR {pnr_number} not found.")
    except Error as e:
        print(f"Database error while checking status: {e}")
    finally:
        cursor.close()
def cancel_ticket(conn, pnr_number):
    cursor = conn.cursor()
    try:
        sql_select = "SELECT train_id, pnr_number, status,seat_type FROM Tickets WHERE pnr_number = %s"
        cursor.execute(sql_select, (pnr_number,))
        result = cursor.fetchone()  
        if result:
            train_id, pnr_db, status,seat_type = result 
            if False:
                print(f"Error: Ticket with PNR {pnr_db} is already cancelled.")
                return False
            sql_update_ticket = "UPDATE Tickets SET status = 'CANCELLED' WHERE pnr_number = %s"
            cursor.execute(sql_update_ticket, (pnr_number,))
            cursor.execute("UPDATE Train SET available_seats = available_seats + 1 WHERE train_id = '%s'",(train_id,))
            if seat_type=="AC":
                cursor.execute("UPDATE Train SET ac_seats = ac_seats + 1 WHERE train_id = '%s'",(train_id,))
            if seat_type=="Non-AC":
                cursor.execute("UPDATE Train SET Non_ac_seats = Non_ac_seats + 1 WHERE train_id = '%s'",(train_id,))
            conn.commit()
            print(f"Ticket with PNR {pnr_db} has been cancelled successfully.")
            return True
        else:
            print(f"Error: Ticket with PNR {pnr_number} not found.")
            return False
    except Error as e:
        conn.rollback() 
        print(f"Database error during cancellation: {e}")
        return False
    finally:
        cursor.close()
def display_food(conn):
    cursor = conn.cursor()
    try:
        sql = "SELECT Food_id,Food_Name,Price,Quantity FROM Catering WHERE Quantity > 0"
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            print("\n")
            print(" "*18," Available Food ")
            print("-"*58)
            print(f"{'ID':<4} | {'Name':<20} | {'Price':<15} | {'Quantity':<9} |")
            print("-" * 58)
            for row in results:
                print(f"{row[0]:<4} | {row[1]:<20} | {row[2]:<15} | {row[3]:<9} |")
                print("-"*58)
        else:
            print("No Food available at the moment.")
    except Error as e:
        print(f"Error fetching Train: {e}")
    finally:
        cursor.close()
def order_food(conn, pnr_number, train_id, passenger_name, food_id, seat_type, qty):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Quantity FROM Catering WHERE Food_id = %s",(food_id,))
        result = cursor.fetchone()
        if result and result[0] >= qty:
            cursor.execute("""INSERT INTO Orders(train_id, passanger_name, food_id, quantity,status, pnr_number, seat_type VALUES (%s,%s,%s,%s,'CONFIRMED',%s,%s)""", (train_id, passenger_name, food_id,qty, pnr_number, seat_type))
            cursor.execute("UPDATE Catering SET Quantity = Quantity - %s WHERE Food_id = %s",(qty, food_id))
            conn.commit()
            print("Food ordered successfully!")
        elif result:
            print("Requested quantity is not available.")
        else:
            print("Food item not found.")
    except Error as e:
        conn.rollback()
        print(f"Database error during food order: {e}")
    finally:
        cursor.close()
def food_status(conn, pnr_number):
    cursor = conn.cursor()
    try:
        sql = "SELECT pnr_number, passanger_name, food_id, status,seat_type,Quantity FROM Orders WHERE pnr_number = %s"
        cursor.execute(sql, (pnr_number,))
        result = cursor.fetchone()
        if result:
            pnr , name, food_id, status , seat_type , qty= result
            print("\n--- Food Details---")
            print(f"PNR Number: {pnr}")
            print(f"Status: {status}")
            print(f"Passenger: {name}")
            print(f"Food ID: {food_id}")
            print(f"Quantity: {qty}")
            print(f"Your Seat type: {seat_type}")
            print("----------------------")
        else:
            print(f"Error: Food with PNR {pnr_number} not found.")
    except Error as e:
        print(f"Database error while checking status: {e}")
    finally:
        cursor.close()
def cancel_food(conn, pnr_number):
    cursor = conn.cursor()
    try:
        sql_select = "SELECT Food_id,train_id, pnr_number, status,seat_type FROM Orders WHERE pnr_number = %s"
        cursor.execute(sql_select, (pnr_number,))
        result = cursor.fetchone()  
        if result:
            food_id,train_id, pnr_db, status,seat_type = result 
            if False:
                print(f"Error: Food ordered with PNR {pnr_db} is already cancelled.")
                return False
            sql_update_stat = "UPDATE orders SET status = 'CANCELLED' WHERE pnr_number = %s"
            cursor.execute(sql_update_stat, (pnr_number,))
            cursor.execute("UPDATE catering SET quantity = quantity + 1 WHERE  Food_id = %s",(food_id,))
            conn.commit()
            print(f"Food with PNR {pnr_db} has been cancelled successfully.")
            return True
        else:
            print(f"Error: Food with PNR {pnr_number} not found.")
            return False
    except Error as e:
        conn.rollback() 
        print(f"Database error during cancellation: {e}")
        return False
    finally:
        cursor.close()
def main():
    conn = connect_db()
    if conn:
        create_database_and_tables(conn)
        while True:
            print("\n===== Railway Reservation System =====")
            print("1. Display Train")
            print("2. Book a Ticket")
            print("3. Check Ticket Status")
            print("4. Cancel Ticket")
            print("5. Catering")
            print("6. Order Food")
            print("7. Check Status of Food")
            print("8. Cancel Food")
            print("9. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                display_Train(conn)
            elif choice == '2':
                try:
                    train_id = int(input("Enter Train ID: "))
                    name =input("Enter Passenger Name: ")
                    age = int(input("Enter Passenger Age: "))
                    seat_type=input("Enter Seat Type (AC/Non-AC): ")
                    book_ticket(conn, train_id, name, age,seat_type)
                except ValueError:
                    print("Invalid input for Train ID or Age. Please enter numbers.")
            elif choice == '3':
                pnr = input("Enter PNR Number: ")
                check_ticket_status(conn, pnr)
            elif choice == '4':
                pnr = input("Enter PNR Number to cancel: ")
                cancel_ticket(conn, pnr)
            elif choice == '5':
                display_food(conn)
            elif choice == '6':
                try:
                    cursor=conn.cursor()
                    pnr_number=input("Enter Your PNR Number: ")
                    cursor.execute("SELECT status FROM Tickets WHERE pnr_number = %s",(pnr_number,))
                    ticket = cursor.fetchone()
                    if ticket is None:
                        print("Invalid PNR Number. Ticket not found.")
                        return
                    if ticket[0] == "CANCELLED":
                        print("Ticket is cancelled. You cannot order food.")
                        return
                    train_id = int(input("Enter Train ID: "))
                    name =input("Enter Passenger Name: ")
                    Food_id = int(input("Enter Food ID: "))
                    qty=int(input("Enter Quantity: "))
                    seat_type=input("Enter Seat Type (AC/Non-AC): ")
                    order_food(conn,pnr_number, train_id, name, Food_id,seat_type,qty)
                except ValueError:
                    print("Invalid input for Train ID or Age. Please enter numbers.")
            elif choice == '7':
                pnr = input("Enter PNR Number: ")
                food_status(conn, pnr)
            elif choice == '8':
                pnr = input("Enter PNR Number to cancel: ")
                cancel_food(conn, pnr)
            elif choice == '9':
                print("Thank you for using the system!")
                break
            else:
                print("Invalid choice. Please try again.")
        conn.close() 
main()
