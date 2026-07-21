import streamlit as st
st.title("BIO-DATA")
name = st.text_input("Enter your Name")
age = st.number_input("Enter your Age", min_value=10, max_value=70)
user_class = st.selectbox("Select your Class", ["5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th", "Graduation", "Post Graduation"])
ch = st.text_input("School/College")
if ch == "School":
    school = st.text_input("Enter your School Name")
elif ch == "College":
    college = st.text_input("Enter your College Name")
else:
    st.info("Please type 'School' or 'College' above to proceed.")
