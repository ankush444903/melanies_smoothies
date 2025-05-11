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

# Load Fruit Options with SEARCH_ON
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(
    col("FRUIT_NAME"), col("SEARCH_ON")
)
pd_df = my_dataframe.to_pandas()  # Convert to pandas for lookup

# Get list of fruit names
fruit_names = pd_df["FRUIT_NAME"].tolist()

# Multi-select for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_names,
    max_selections=5
)

if ingredients_list:
    # Generate string for DB entry
    ingredients_string = ", ".join(ingredients_list)

    # Submit order to Snowflake
    if st.button("Submit Order"):
        session.sql(f"""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (name_on_order, ingredients)
            VALUES ('{name_on_order}', '{ingredients_string}')
        """).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

    # Display nutrition info from both APIs
    for fruit_chosen in ingredients_list:
        # Get SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Smoothiefroot API
        try:
            sf_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on.lower()}")
            if sf_response.status_code == 200:
                st.write("📊 From Smoothiefroot:")
                st.dataframe(data=sf_response.json(), use_container_width=True)
            else:
                st.warning(f"Smoothiefroot: No data for {fruit_chosen}")
        except Exception as e:
            st.error(f"Smoothiefroot API error for {fruit_chosen}: {e}")

        # Fruitvvice API
        try:
            fv_response = requests.get(f"https://fruitvvice.com/api/fruit/{search_on}")
            if fv_response.status_code == 200:
                st.write("📊 From Fruitvvice:")
                st.dataframe(data=fv_response.json(), use_container_width=True)
            else:
                st.warning(f"Fruitvvice: No data for {fruit_chosen}")
        except Exception as e:
            st.error(f"Fruitvvice API error for {fruit_chosen}: {e}")
