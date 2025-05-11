# Import packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App title and instructions
st.title("🥤 My Parents' New Healthy Diner! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name on smoothie input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Create connection using Streamlit's native connection manager
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Get fruit options from Snowflake
fruit_df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col('FRUIT_NAME')).to_pandas()
fruit_names = fruit_df['FRUIT_NAME'].tolist()

# Multi-select for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

# Process order
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)

    if st.button("Submit Order"):
        # Insert order into Snowflake
        session.sql(f"""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (name_on_order, ingredients)
            VALUES ('{name_on_order}', '{ingredients_string}')
        """).collect()

        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json)
