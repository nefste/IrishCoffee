# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 14:54:51 2023

@author: 061246848
"""


import streamlit as st
import pandas as pd
from datetime import datetime



st.set_page_config(
    page_title="Fenelons Irish Coffee",
    page_icon="🪖",
)


streamlit_style = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100&display=swap');

			html, body, [class*="css"]  {
			font-family: 'Roboto';
			}
			</style>
			"""
st.markdown(streamlit_style, unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# Function to add a new user to the Excel file
def add_user_to_excel(new_user_data):
    try:
        users_df = pd.read_excel('users.xlsx')
    except FileNotFoundError:
        users_df = pd.DataFrame(columns=['username', 'weight', 'age'])

    # Create a DataFrame for the new user data
    new_user_df = pd.DataFrame([new_user_data])

    # Use concat instead of append
    users_df = pd.concat([users_df, new_user_df], ignore_index=True)
    users_df.to_excel('users.xlsx', index=False)


# Page Title
st.title("User Registration")

# Registration Form
with st.form("user_registration_form"):
    username = st.text_input("Name", placeholder="Stephan Nef")
    weight = st.number_input("Weight (kg)", min_value=35, step=5)
    age = st.number_input("Age", min_value=14, max_value=120, step=1)
    submit_button = st.form_submit_button("Register")

# Handle form submission
if submit_button:
    if username and weight > 0 and age > 0:
        # Check if username already exists
        users_df = pd.read_excel('users.xlsx')
        if username in users_df['username'].values:
            st.error(f"Username '{username}' already exists. Please choose a different username.")
        else:
            new_user_data = {'username': username, 'weight': weight, 'age': age}
            add_user_to_excel(new_user_data)
            st.success(f"User {username} registered successfully!")

    else:
        # Handle case where input data is not valid
        st.error("Please enter a valid username, weight, and age.")


# Optional: Display current users
if st.checkbox("Show Registered Users"):
    try:
        users_df = pd.read_excel('users.xlsx')
        st.write(users_df)
    except FileNotFoundError:
        st.write("No users registered yet.")
