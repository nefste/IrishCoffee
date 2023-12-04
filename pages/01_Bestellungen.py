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
    page_icon="🍀",
)


hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# Load the existing orders from the Excel file
orders_df = pd.read_excel('orders.xlsx')

# Function to update order status
def update_order_status(selected_indices, new_status):
    global orders_df
    orders_df.loc[selected_indices, 'status'] = new_status
    orders_df.to_excel('orders.xlsx', index=False)

# Display the orders in a table with checkboxes
st.title("👨🏿‍🍳 Order Management")
st.subheader("Select orders to mark as prepared:")

# Sort orders by timestamp
orders_df = orders_df.sort_values(by='timestamp', ascending=False)

# Add a column for checkboxes
orders_df['select'] = False

# Display the dataframe with checkboxes
df_display = st.checkbox("Show only unprepared orders",value=True)
if df_display:
    df = orders_df[orders_df['status'] == 'ordered']
else:
    df = orders_df

df = df.reset_index()
selected_indices = st.multiselect('Select Orders', df.index, format_func=lambda x: f"Order {x} - {df.loc[x, 'drink']} by {df.loc[x, 'username']}")

# Button to update the status of selected orders
if st.button("Mark as Prepared"):
    update_order_status(selected_indices, "prepared")
    st.success(f"Updated {len(selected_indices)} orders to 'prepared' status.")


st.subheader("Overview of Orders")

with st.expander("Open Orders"):
    st.dataframe(orders_df[orders_df['status'] == 'ordered'])

with st.expander("Prepared Orders"):
    st.dataframe(orders_df[orders_df['status'] == 'prepared'])

with st.expander("Consumed Orders"):
    st.dataframe(orders_df[orders_df['status'] == 'consumed'])