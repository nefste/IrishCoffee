# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 14:54:51 2023

@author: 061246848
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Set page config
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

# Load data from Excel files
orders_df = pd.read_excel('orders.xlsx')
users_df = pd.read_excel('users.xlsx')



# Initialize a DataFrame to hold the BAC levels with a common time index
timestamps = pd.date_range(start=orders_df['timestamp'].min(), end=orders_df['consumed_time'].max(), freq='1T')
bac_tracking = pd.DataFrame(index=timestamps)

# Populate the DataFrame with BAC levels for each user
for user in users_df.to_dict('records'):
    username = user['username']
    user_orders = orders_df[(orders_df['username'] == username) & (orders_df['status'] == 'consumed')]

    if not user_orders.empty:
        user_orders = user_orders.sort_values(by='timestamp')
        # Reindex the user orders to the common time index with forward fill to carry the last known BAC value
        user_bac = user_orders.set_index('timestamp')['bac'].reindex(timestamps, method='ffill')
        bac_tracking[username] = user_bac

# Drop any columns that are all NaN, which can occur if a user has no orders
bac_tracking = bac_tracking.dropna(axis=1, how='all')

# Now plot the BAC data using Plotly
st.title("📈 BAC Levels Over Time")

if not bac_tracking.empty:
    fig = px.line(bac_tracking, x=bac_tracking.index, y=bac_tracking.columns,
                  labels={'value': 'BAC', 'variable': 'User', 'index': 'Timestamp'},
                  title='BAC Levels Over Time for Each User')
    st.plotly_chart(fig)
else:
    st.write("No BAC data available to display.")


st.subheader("🏆 Leaderboard")
st.write("TO BE DONE")

st.write("---")







# Refresh Button
if st.button('Refresh Data'):
    st.experimental_rerun()









