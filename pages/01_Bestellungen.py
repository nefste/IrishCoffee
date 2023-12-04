# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 14:54:51 2023

@author: 061246848
"""

import streamlit as st
import pandas as pd
from datetime import datetime
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

# Load the existing orders from the Excel file
orders_df = pd.read_excel('orders.xlsx')

# Function to update order status
# Function to update order status
def update_order_status(selected_indices, new_status):
    global orders_df
    orders_df.loc[selected_indices, 'status'] = new_status
    orders_df.to_excel('orders.xlsx', index=False)
    # Reload the updated orders dataframe immediately after saving
    orders_df = pd.read_excel('orders.xlsx')
    st.success(f"Updated {len(selected_indices)} orders to '{new_status}' status.")



# Display the orders in a table with checkboxes
st.title("👨🏿‍🍳 Order Management")
st.subheader("Select orders to mark as prepared:")

# Sort orders by timestamp
orders_df = orders_df.sort_values(by='timestamp', ascending=False)

# Filter the DataFrame to show only 'ordered' or all orders based on checkbox
df_display = st.checkbox("Show only unprepared orders", value=True)
if df_display:
    df = orders_df[orders_df['status'] == 'ordered']
else:
    df = orders_df

# Use a form for the order update process
with st.form("update_order_form"):
    df = df.reset_index()
    # Create a multiselect box to select orders to be prepared
    selected_indices = st.multiselect(
        'Select Orders', 
        df.index, 
        format_func=lambda x: f"Order {x} - {df.loc[x, 'drink']} by {df.loc[x, 'username']}"
    )
    # Create a submit button for the form
    submit_button = st.form_submit_button("Mark as Prepared")

    if submit_button:
        # If no orders selected, prompt user to select orders
        if not selected_indices:
            st.warning("Please select at least one order to mark as prepared.")
        else:
            update_order_status(selected_indices, "prepared")

# Refresh the page to reflect the updates
if 'refresh' in st.session_state and st.session_state['refresh']:
    st.session_state['refresh'] = False
    st.experimental_rerun()


st.subheader("Overview of Orders")

with st.expander("Open Orders"):
    st.dataframe(orders_df[orders_df['status'] == 'ordered'])

with st.expander("Prepared Orders"):
    st.dataframe(orders_df[orders_df['status'] == 'prepared'])

with st.expander("Consumed Orders"):
    st.dataframe(orders_df[orders_df['status'] == 'consumed'])
    

# Refresh the page
if 'refresh' not in st.session_state:
    st.session_state['refresh'] = False
    
if st.session_state['refresh']:
    st.session_state['refresh'] = False  # Reset the refresh state
    st.experimental_rerun()

if st.button("Refresh Page"):
    st.session_state['refresh'] = True
