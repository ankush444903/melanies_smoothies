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

# Load fruit data with SEARCH_ON from Snowflake
my_dataframe = session.table('SMOOTHIES.PUBLIC.FRUIT_OPTIONS').select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)

# Convert Snowpark DataFrame to Pandas
pd_df = my_dataframe.to_pandas()

# Show fruit options in multiselect
fruit_names = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

# If user selected fruits
if ingredients_list:
    # Convert ingredients list to comma-separated string
    ingredients_string = ', '.join(ingredients_list)

    # Submit button to place the order
    if st.button("Submit Order"):
        session.sql(f"""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (name_on_order, ingredients)
            VALUES ('{name_on_order}', '{ingredients_string}')
        """).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

    # Show nutrition information from fruityvice
    st.subheader("🍓 Nutritional Info from Fruityvice API")
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Get the 'SEARCH_ON' value for API call
        try:
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            api_fruit_name = search_on.lower().replace(" ", "%20")

            response = requests.get(f"https://fruityvice.com/api/fruit/{api_fruit_name}")

            if response.status_code == 200:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.warning(f"No nutrition data available for: {fruit_chosen}")
        except Exception as e:
            st.error(f"Error fetching Fruityvice data for {fruit_chosen}: {e}")
