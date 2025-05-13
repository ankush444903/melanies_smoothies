# Import packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App title and input
st.title("🥤 My Parents' New Healthy Diner! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Load fruit data
fruit_df = session.table('SMOOTHIES.PUBLIC.FRUIT_OPTIONS').select(
    col('FRUIT_NAME'), col('SEARCH_ON')
).to_pandas()

# Multiselect options
fruit_names = fruit_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

# Submit order
if st.button("Submit Order"):
    if not name_on_order:
        st.warning("Please enter your name to place an order.")
    elif not ingredients_list:
        st.warning("Please select at least one ingredient.")
    else:
        # Convert selected fruits to a SQL-compatible array string
        ingredients_sql_array = ",".join(f"'{item}'" for item in ingredients_list)

        insert_sql = f"""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (name_on_order, ingredients)
            SELECT '{name_on_order}' AS name_on_order, ARRAY_CONSTRUCT({ingredients_sql_array}) AS ingredients
        """
        session.sql(insert_sql).collect()  # Run the SQL

        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

        # Show nutrition info
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
