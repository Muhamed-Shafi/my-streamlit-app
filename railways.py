import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
import random

st.set_page_config(page_title="Railway Reservation System",page_icon="🚆",layout="wide")
def connect_db():
    try:
        conn = mysql.connector.connect(host="localhost",database="railway",user="root",password="123456") 
        return conn
    except Error as e:
        st.error(e)
        return None
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Train(Train_id INT AUTO_INCREMENT PRIMARY KEY,Train_name VARCHAR(100),Source VARCHAR(100),Destination VARCHAR(100),Total_seats INT,Available_seats INT,Boarding_time DATETIME,Arrival_time DATETIME,AC_Seats INT,Non_AC_Seats INT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Tickets(Pnr_number VARCHAR(10) PRIMARY KEY,Train_id INT,Passenger_name VARCHAR(100),Passenger_age INT,Status VARCHAR(20) DEFAULT 'CONFIRMED',Booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,Seat_type VARCHAR(30),FOREIGN KEY(Train_id) REFERENCES Train(Train_id))""")
    conn.commit()
    cursor.close()
    conn.close()
create_tables()
st.title("🚆 Railway Reservation System")
menu = st.sidebar.radio("Select Menu",("Home","Display Trains","Book Ticket","Check Ticket Status","Cancel Ticket","Display Food","Order Food","Check Food Status","Cancel Food","Journey Map" ))
if menu == "Home":
    st.header("Welcome")
    st.image("https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=1200",use_container_width=True)
elif menu == "Display Trains":
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT Train_id,Train_name,Source,Destination,Available_seats,AC_Seats,Non_AC_Seats,Boarding_time,Arrival_time FROM Train""")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    if data:
        df = pd.DataFrame(data,columns=["Train ID","Train","Source","Destination","Available","AC","Non AC","Boarding","Arrival"])
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No Train Available")
elif menu == "Book Ticket":
    st.header("Book Ticket")
    train_id = st.number_input("Train ID",min_value=1,step=1)
    passenger = st.text_input("Passenger Name")
    age = st.number_input("Age",min_value=1,max_value=120)
    seat = st.selectbox("Seat Type",("AC","Non-AC"))
    if st.button("Book Ticket (Click Once)"):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""SELECT Available_seats,AC_Seats,Non_AC_Seats FROM Train WHERE Train_id=%s""",(train_id,))
        row = cursor.fetchone()
        if row:
            available, ac, nonac = row
            if available <= 0:
                st.error("No Seats Available")
            else:
                if seat == "AC" and ac <= 0:
                    st.error("AC Seats Full")
                elif seat == "Non-AC" and nonac <= 0:
                    st.error("Non AC Seats Full")
                else:
                    pnr = "PNR" + str(random.randint(100000,999999))
                    cursor.execute("""INSERT INTO Tickets(Pnr_number,Train_id,Passenger_name,Passenger_age,Seat_type)VALUES(%s,%s,%s,%s,%s)""",(pnr,train_id,passenger,age,seat))
                    cursor.execute("""UPDATE Train SET Available_seats=Available_seats-1 WHERE Train_id=%s""",(train_id,))
                    if seat=="AC":
                        cursor.execute("""UPDATE Train SET AC_Seats=AC_Seats-1 WHERE Train_id=%s""",(train_id,))
                    else:
                        cursor.execute("""UPDATE Train SET Non_AC_Seats=Non_AC_Seats-1 WHERE Train_id=%s""",(train_id,))
                    conn.commit()
                    st.success("Ticket Booked Successfully")
                    st.info(f"Your PNR Number : {pnr}")
        else:
            st.error("Invalid Train ID")
        cursor.close()
        conn.close()

elif menu == "Check Ticket Status":
    st.header("Ticket Status")
    pnr = st.text_input("Enter PNR Number")
    if st.button("Check My Status"):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""SELECT T.Pnr_number, T.Passenger_name,T.Passenger_age, T.Status, T.Seat_type, Tr.Train_name, Tr.Source, Tr.Destination FROM Tickets T JOIN Train Tr ON T.Train_id=Tr.Train_id WHERE T.Pnr_number=%s""",(pnr,))
        row = cursor.fetchall()
        if row:
            df=pd.DataFrame(row,columns=["PNR","Passenger Name","Age","Status","Seat Type","Train Name","Source","Destination"])
            st.dataframe(df, use_container_width=True)
        else:
            st.error("Ticket Not Found")
        cursor.close()
        conn.close()

elif menu=="Cancel Ticket":
    st.header("Cancel Ticket")
    pnr=st.text_input("PNR Number")
    if st.button("Cancel My Ticket"):
        conn=connect_db()
        cursor=conn.cursor()
        cursor.execute("""SELECT Train_id,Seat_type, Status FROM Tickets WHERE Pnr_number=%s""",(pnr,))
        row=cursor.fetchone()
        if row:
            train_id,seat,status=row
            if status=="CANCELLED":
                st.warning("Already Cancelled")
            else:
                cursor.execute("""UPDATE Tickets SET Status='CANCELLED' WHERE Pnr_number=%s""",(pnr,))
                cursor.execute("""UPDATE Train SET Available_seats=Available_seats+1 WHERE Train_id=%s""",(train_id,))
                if seat=="AC":
                    cursor.execute("""UPDATE Train SET AC_Seats=AC_Seats+1 WHERE Train_id=%s""",(train_id,))
                else:
                    cursor.execute("""UPDATE Train SET Non_AC_Seats=Non_AC_Seats+1 WHERE Train_id=%s""",(train_id,))
                conn.commit()
                st.success("Ticket Cancelled Successfully")
        else:
            st.error("PNR Not Found")
        cursor.close()
        conn.close()
        
elif menu == "Display Food":
    st.header("Available Food")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Catering(Food_id INT AUTO_INCREMENT PRIMARY KEY,Food_Name VARCHAR(100),Price DECIMAL(10,2),Quantity INT)""")
    conn.commit()
    cursor.execute("""SELECT Food_id,Food_Name,Price,Quantity FROM Catering""")
    rows = cursor.fetchall()
    if rows:
        df = pd.DataFrame(rows,columns=["Food ID","Food Name","Price","Quantity"])
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No Food Available")
    cursor.close()
    conn.close()

elif menu == "Order Food":
    st.header("Order Food") 
    pnr = st.text_input("PNR Number")
    food_id = st.number_input("Food ID",min_value=1,step=1)
    qty = st.number_input("Quantity",min_value=1,step=1)
    if st.button("Click here toOrder"):
        conn = connect_db()
        cursor = conn.cursor(buffered=True)
        cursor.execute("""SELECT Train_id,Passenger_name,Seat_type,Status FROM Tickets WHERE Pnr_number = %s""", (pnr,))
        ticket = cursor.fetchone()
        if ticket is None:
            st.error("Invalid PNR")
        else:
            train_id = ticket[0]
            passenger_name = ticket[1]
            seat_type = ticket[2]
            status = ticket[3]
            if status == "CANCELLED":
                st.error("Ticket is Cancelled")
            else:
                cursor.execute("""SELECT Quantity FROM Catering WHERE Food_id = %s""", (food_id,))
                food = cursor.fetchone()
                if food is None:
                    st.error("Food Item Not Found")
                elif food[0] < qty:
                    st.warning("Insufficient Quantity")
                else:
                    cursor.execute("""INSERT INTO Orders(Train_id,Passanger_name,Food_id,Quantity,Status,Pnr_number,Seat_type) VALUES(%s,%s,%s,%s,'CONFIRMED',%s,%s)""",(train_id, passenger_name,food_id,qty, pnr,seat_type))
                    cursor.execute("""UPDATE Catering SET Quantity = Quantity - %s WHERE Food_id = %s""", (qty, food_id))
                    conn.commit()
                    st.success("Food Ordered Successfully")
        cursor.close()
        conn.close()
 
elif menu == "Check Food Status":
    st.header("Food Status")
    pnr = st.text_input("Enter PNR")
    if st.button("Check My Food Status"):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""SELECT O.Pnr_number, C.Food_Name, O.Quantity, O.Status FROM Orders O JOIN Catering C ON O.Food_id=C.Food_id WHERE O.Pnr_number=%s""",(pnr,))
        rows = cursor.fetchall()
        if rows:
            st.success("Orders Found")
            df = pd.DataFrame(rows,columns=["PNR","Food Name","Quantity","Status"])
            st.dataframe(df, use_container_width=True)
        else:
            st.error("No Order Found")

elif menu == "Cancel Food":
    st.header("Cancel Food")
    pnr = st.text_input("PNR")
    if st.button("Cancel My Food for Some Reason"):
        conn = connect_db()
        cursor = conn.cursor(buffered=True)
        cursor.execute("""SELECT Food_id,Quantity,Status FROM Orders WHERE Pnr_number=%s LIMIT 1""", (pnr,))
        row = cursor.fetchone()
        if row is None:
            st.error("Order Not Found")
        else:
            food_id, qty, status = row
            if status == "CANCELLED":
                st.warning("Order Already Cancelled")
            else:
                cursor.execute("""UPDATE Orders SET Status='CANCELLED' WHERE Pnr_number=%s""", (pnr,))
                cursor.execute("""UPDATE Catering SET Quantity = Quantity + %s WHERE Food_id = %s""", (qty, food_id))
                conn.commit()
                st.success("Food Order Cancelled Successfully")
        cursor.close()
        conn.close()

elif menu == "Journey Map":
    import folium
    from streamlit_folium import st_folium
    from geopy.geocoders import Nominatim
    st.header("🚆 Journey Map")
    pnr = st.text_input("Enter PNR Number")
    if pnr:
        conn = connect_db()
        cursor = conn.cursor(buffered=True)
        cursor.execute("""SELECT T.Source, T.Destination FROM Train T JOIN Tickets Tk ON T.Train_id = Tk.Train_id WHERE Tk.Pnr_number = %s""", (pnr,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            source = row[0]
            destination = row[1]
            geolocator = Nominatim(user_agent="railway")
            src = geolocator.geocode(source)
            dst = geolocator.geocode(destination)
            if src and dst:
                st.success(f"{source} ➜ {destination}")
                m = folium.Map(location=[ (src.latitude + dst.latitude) / 2,(src.longitude + dst.longitude) / 2], zoom_start=6)
                folium.Marker([src.latitude, src.longitude],popup=source, tooltip="Source").add_to(m)
                folium.Marker([dst.latitude, dst.longitude],popup=destination,tooltip="Destination").add_to(m)
                folium.PolyLine( [ [src.latitude, src.longitude],[dst.latitude, dst.longitude]], color="red", weight=5).add_to(m)
                st_folium(m,width=900,height=500,returned_objects=[])
            else:
                st.error("Unable to locate one of the cities.")
        else:
            st.error("Invalid PNR Number")

st.sidebar.markdown("---")
st.sidebar.success("Railway Reservation System")
