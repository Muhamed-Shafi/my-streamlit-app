import streamlit as st
import requests
import pandas as pd

st.title("🌤️ Real-Time Weather Tracker")

city = st.text_input("Enter City Name:")

@st.fragment(run_every=5)
def auto_updating_weather(city_name):
    if city_name:
        try:
            url = f"https://wttr.in/{city_name}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:        # code 200 means "OK"
                data = response.json()             # Converts raw data into a Python dictionary
                
                # 1. Extract Current Metrics
                current_condition = data["current_condition"][0]
                temp_c = int(current_condition["temp_C"])
                weather_desc = current_condition["weatherDesc"][0]["value"]
                humidity = current_condition["humidity"]
                
                # Display metrics in columns
                col1, col2 = st.columns(2)
                col1.metric(label=f"Current Temp in {city_name}", value=f"{temp_c} °C")
                col2.metric(label="Condition / Humidity", value=f"{weather_desc}", delta=f"{humidity}% Humid")
                
                # 2. Extract Hourly Forecast Timeline for Charting
                # wttr.in gives hourly forecast segments divided into 3-hour blocks (0, 300, 600... up to 2100)
                today_forecast = data["weather"][0]["hourly"]
                
                timeline_data = []
                for block in today_forecast:
                    # Convert raw time strings like '300' or '1200' to clean display labels like '03:00' or '12:00'
                    raw_time = int(block["time"])
                    formatted_time = f"{raw_time//100:02d}:00"
                    
                    block_temp = int(block["tempC"])
                    timeline_data.append({"Time": formatted_time, "Temperature (°C)": block_temp})
                
                # Convert the list into a structured DataFrame
                df = pd.DataFrame(timeline_data)
                df.set_index("Time", inplace=True)
                
                # 3. Render the Line Chart directly below the metrics
                st.subheader("📈 Temperature Trend Timeline")
                st.line_chart(df)
                
            else:
                st.error("Could not fetch data for this location.") 
        except Exception as e:
            st.error(f"Error communicating with the live weather server: {e}")

# Call the auto-refreshing fragment
auto_updating_weather(city)
