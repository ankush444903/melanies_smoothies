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

# Load fruit data from Snowflake
fruit_df = session.table('SMOOTHIES.PUBLIC.FRUIT_OPTIONS').select(
    col('FRUIT_NAME'), col('SEARCH_ON')
).to_pandas()

# Show fruit options in multiselect
fruit_names = fruit_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

# Only proceed if there are ingredients and a name
if st.button("Submit Order"):
    if not name_on_order:
        st.warning("Please enter your name to place an order.")
    elif not ingredients_list:
        st.warning("Please select at least one ingredient.")
    else:
        # Convert to SQL array using ARRAY_CONSTRUCT inside SELECT
        array_construct_query = f"""
            SELECT ARRAY_CONSTRUCT({', '.join(f"'{item}'" for item in ingredients_list)}) AS ingredients_array
        """
        ingredients_array = session.sql(array_construct_query).collect()[0]['INGREDIENTS_ARRAY']

        # Insert using Snowpark API
        session.table("SMOOTHIES.PUBLIC.ORDERS").insert({
            "name_on_order": name_on_order,
            "ingredients": ingredients_array
        })

        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

        # Show nutritional info
        st.subheader("🍓 Nutritional Info from Fruityvice API")
        for fruit in ingredients_list:
            st.subheader(f"{fruit} Nutrition Information")

            try:
                search_on = fruit_df.loc[fruit_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
                api_fruit_name = search_on.lower().replace(" ", "%20")

                response = requests.get(f"https://fruityvice.com/api/fruit/{api_fruit_name}")
                if response.status_code == 200:
                    st.dataframe(data=response.json(), use_container_width=True)
                else:
                    st.warning(f"No nutrition data available for: {fruit}")
            except Exception as e:
                st.error(f"Error fetching data for {fruit}: {e}")
