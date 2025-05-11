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

# Submit Order and Show Nutritional Info
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)

    # Submit to Snowflake Orders table
    if st.button("Submit Order"):
        session.sql(f"""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (name_on_order, ingredients)
            VALUES ('{name_on_order}', '{ingredients_string}')
        """).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

    # Nutritional Info Section
    st.subheader("🍓 Nutritional Info from Smoothiefroot API")
    for fruit_chosen in ingredients_list:
        # Get value from SEARCH_ON column
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f"The search value for {fruit_chosen} is: `{search_on}`")

        # Call API using the SEARCH_ON value
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on.lower()}")
            if response.status_code == 200:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.warning(f"No nutrition data available for: {fruit_chosen}")
        except Exception as e:
            st.error(f"Failed to fetch data for {fruit_chosen}: {e}")
