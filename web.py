import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np
st.title("WELCOME TO MY WEB")
st.write("Hello World")
st.header("Streamlit tutorial")
st.subheader("Sub header")
st.text("Write text")
st.markdown("From Markdown")
st.caption("Captions")

df=pd.DataFrame({"Name":["Code","Solve","Execute"],"Marks":[100,200,300]})
st.write(df)
st.dataframe(df)
st.write("This is Table")
st.table(df)

name=st.text_input("Enter Your Name: ")
age=st.number_input("Enter Your Age: ",min_value=10,max_value=20)

rating=st.slider("Rate your experience: ",0,10,5)
color=st.selectbox("Pick a color: ",["Red","Green","Blue"])

if st.checkbox("Show Message"):
    st.write("HI")

ch=st.radio("Pick One: ",["1","2","3"]) 

img=Image.open("C:\\Users\\DELL RYZEN\\OneDrive\\Desktop\\VS\\Screenshot 2025-12-25 111516.png")
st.image(img,caption="Sample Image")

#st.audio("url")
#st.video("url")

st.sidebar.title("CODE SOLVE")
name=st.sidebar.text_input("Enter Your Name: ")


col1,col2=st.columns(2)
col1.write("col1")
col2.write("col2")

with st.expander("See More"):
    st.write("HI CSE")

up=st.file_uploader("Upload CSV File",type=["csv"])

import time
my_bar=st.progress(0)
for i in range(100):
    time.sleep(0.05)
    my_bar.progress(i+1)

st.success("Success")
st.error("Error")
st.warning("Warning")
st.info("Information")

if st.button("Click Me"):
    st.write("Button Clicked")

with st.form("Bio-data"):
    name=st.text_input("Enter Your Name: ")
    age=st.number_input("Enter Your Age: ",min_value=10,max_value=20) 
    submit_button=st.form_submit_button("Submit")
    if submit_button:
        st.write(f"Hello {name}, your age is {age}")


data=pd.DataFrame(np.random.randn(10,3),columns=["A","B","C"])
st.line_chart(data)
st.bar_chart(data)
st.area_chart(data)

map_data=pd.DataFrame(np.random.randn(100,2)/[50,50]+[37.76,-122.4],columns=["lat","lon"])
st.map(map_data)

@st.cache_data
def add(x):
    return x+2

resl=add(3)
st.write(resl)