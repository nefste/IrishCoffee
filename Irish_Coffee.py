# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="Fenelons Irish Coffee",
    page_icon="🍀",
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


if 'refresh' not in st.session_state:
    st.session_state['refresh'] = False


# Sample data structure for drinks
drinks = {
    "Irish Coffee": {"standard": {"abv": 18, "volume_ml": 250},
                     "with_whipped_cream": {"abv": 18, "volume_ml": 250},
                     "without_whipped_cream": {"abv": 18, "volume_ml": 250}},
    "Beer": {"standard": {"abv": 4.5, "volume_ml": 300}},
    "Espresso": {"standard": {"abv": 0, "volume_ml": 50}},
    "Normal Coffee": {"standard": {"abv": 0, "volume_ml": 250}},
    "Mineral Water": {"with_gas": {"abv": 0, "volume_ml": 250},
                      "standard": {"abv": 18, "volume_ml": 250},
                      "without_gas": {"abv": 0, "volume_ml": 250}},
    "Orange Juice": {"standard": {"abv": 0, "volume_ml": 250}}
}


# Function to initialize or read Excel files
def init_data():
    try:
        orders_df = pd.read_excel('orders.xlsx')
        users_df = pd.read_excel('users.xlsx')
    except FileNotFoundError:
        orders_df = pd.DataFrame(columns=['username', 'drink', 'timestamp', 'status','volume_ml','abv'])
        users_df = pd.DataFrame(columns=['username', 'weight', 'age'])
        orders_df.to_excel('orders.xlsx', index=False)
        users_df.to_excel('users.xlsx', index=False)
    return orders_df, users_df

orders_df, users_df = init_data()


def calculate_bac(user_weight, drinks_consumed, minutes_since_first_drink):
    # Constants
    widmark_factor = 0.68
    decay_rate_per_minute = 0.0016  # BAC decay rate per minute

    # Calculate total alcohol in grams
    total_alcohol_grams = 0
    for drink in drinks_consumed:
        volume_ml, abv = drink
        alcohol_grams = volume_ml * (abv / 100) * 0.789
        total_alcohol_grams += alcohol_grams

    # Calculate BAC
    body_weight_grams = user_weight * 1000
    raw_bac = (total_alcohol_grams / (body_weight_grams * widmark_factor)) * 100

    # Adjust for metabolism over time
    bac_decay = decay_rate_per_minute * minutes_since_first_drink
    adjusted_bac = max(raw_bac - bac_decay, 0)
    return adjusted_bac



def update_order_status_to_consumed():
    global orders_df, users_df
    now = datetime.now()

    for index, order in orders_df.iterrows():
        if order['status'] == 'prepared':
            order_time = order['timestamp']
            if isinstance(order_time, str):
                order_time = datetime.strptime(order_time, '%Y-%m-%d %H:%M:%S.%f')

            if now - order_time > timedelta(minutes=10):  # Check if 10 minutes have passed since the order was prepared
                username = order['username']
                user_info = users_df[users_df['username'] == username].iloc[0]
                
                # Safeguard against missing drink details
                drink_info = drinks.get(order['drink'], {})
                volume_ml = drink_info.get('volume_ml', 0)  # Default to 0 if not specified
                abv = drink_info.get('abv', 0)  # Default to 0 if not specified

                # Get all past consumed drinks for this user
                user_orders = orders_df[(orders_df['username'] == username) & (orders_df['status'] == 'consumed')]
                all_drinks = [(drink['volume_ml'], drink['abv']) for idx, drink in user_orders.iterrows()]
                all_drinks.append((volume_ml, abv))  # Add the current drink to the list

                # Find the time of the first drink
                first_drink_time = min(user_orders['timestamp'], default=now)
                minutes_since_first_drink = (now - first_drink_time).total_seconds() / 60.0  # Convert to minutes
                bac = calculate_bac(user_info['weight'], all_drinks, minutes_since_first_drink)

                # Update the order with the calculated BAC
                orders_df.at[index, 'bac'] = bac
                orders_df.at[index, 'status'] = 'consumed'
                orders_df.at[index, 'consumed_time'] = now

    orders_df.to_excel('orders.xlsx', index=False)






st.title("🍀 Fenelons Irish Coffee")

open_orders = len(orders_df[orders_df['status'] == 'ordered'])
consumed_irish_coffees = len(orders_df[orders_df['drink'] == 'Irish Coffee'])
# Assuming BAC calculation is implemented in a function calculate_bac()
highest_bac_user = "To Be Calculated"  # Placeholder for highest BAC calculation

col1, col2 = st.columns(2)
col1.metric("Open Orders", open_orders)
consumed_coffees = len(orders_df[orders_df['status'] == 'consumed'])
# Display this metric
col2.metric("Consumed Drinks", consumed_coffees)

# User registration and order placement
with st.form("order_form"):
    st.subheader("☕ Place your Order here")
    username = st.selectbox("Select your name", users_df['username'])
    selected_drink = st.selectbox("Choose your drink", list(drinks.keys()))
    # More options based on drink
    submit_button = st.form_submit_button("Place Order")


# Handle order placement
if submit_button:
    if len(orders_df[(orders_df['username'] == username) & (orders_df['status'] == 'ordered')]) == 0:
        # Extract drink details from the drinks dictionary
        drink_details = drinks[selected_drink]
        variant = "standard"  # Assuming a default variant named 'standard'
        # if isinstance(drink_details, dict):
        #     # If there are variants, you might need to let the user choose
        #     variant = st.selectbox("Choose the variant", list(drink_details.keys()))
        abv = drink_details[variant]['abv']
        volume_ml = drink_details[variant]['volume_ml']

        # Create new order with volume_ml and abv
        new_order = pd.DataFrame([{'username': username, 'drink': selected_drink, 'timestamp': datetime.now(), 'status': 'ordered', 'volume_ml': volume_ml, 'abv': abv}])
        orders_df = pd.concat([orders_df, new_order], ignore_index=True)
        orders_df.to_excel('orders.xlsx', index=False)
        st.success("Order placed successfully!")
        update_order_status_to_consumed()
        time.sleep(3)
        st.session_state['refresh'] = True
    else:
        st.warning("Wooh relax, you already have a drink in order.")





# Refresh the page
if st.session_state['refresh']:
    st.session_state['refresh'] = False  # Reset the refresh state
    update_order_status_to_consumed()
    st.experimental_rerun()

st.write("---")

st.subheader("Overview of Orders")

with st.expander("Open Orders"):
    st.dataframe(orders_df[orders_df['status'] == 'ordered'])

with st.expander("Prepared Orders"):
    st.dataframe(orders_df[orders_df['status'] == 'prepared'])

with st.expander("Consumed Orders"):
    st.dataframe(orders_df[orders_df['status'] == 'consumed'])

if st.button("Refresh Page"):
    st.session_state['refresh'] = True
















