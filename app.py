import streamlit as st
import mariadb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Function to fetch data from MariaDB
def fetch_data():
    try:
        conn = mariadb.connect(
            user="root",
            password="1234",
            host="localhost",
            port=3306,
            database="jumia2"  # Replace with your actual database name
        )
        query = "SELECT * FROM jumia_product"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except mariadb.Error as e:
        st.error(f"Error connecting to the database: {e}")
        return pd.DataFrame()

# Load data
data = fetch_data()

# Data cleaning - replace "No ratings" with 0 and "No discount" with 0
data['Ratings'] = pd.to_numeric(data['Ratings'].replace("No ratings", 0), errors='coerce').fillna(0)
data['Discount'] = pd.to_numeric(data['Discount'].replace("No discount", 0), errors='coerce').fillna(0)

# Streamlit app layout
st.title("Jumia Product Dashboard")
st.write("Analyze pricing trends and discover the best times to buy specific products on Jumia.")

# 1. Bar Chart: Top 10 Products with Highest Discounts
st.header("Top 10 Products with Highest Discounts")
top_discounted = data.nlargest(10, 'Discount')
fig1 = go.Figure(data=[go.Bar(
    x=top_discounted['Name'],
    y=top_discounted['Discount'],
    text=top_discounted['Discount'],
    textposition='auto'
)])
fig1.update_layout(title_text="Top 10 Products with Highest Discounts", xaxis_title="Product Name", yaxis_title="Discount (%)")
st.plotly_chart(fig1)

# 2. Pie Chart: Distribution of Products by Ratings
st.header("Product Distribution by Ratings")
# Categorize ratings into groups for visualization
rating_bins = pd.cut(data['Ratings'], bins=[0, 1, 2, 3, 4, 5], labels=['0-1', '1-2', '2-3', '3-4', '4-5'])
rating_counts = rating_bins.value_counts().sort_index()

fig2 = px.pie(values=rating_counts, names=rating_counts.index, title="Distribution of Products by Ratings")
st.plotly_chart(fig2)

# 3. Pie Chart: Discount Distribution
st.header("Discount Distribution")
# Define discount ranges
discount_bins = pd.cut(data['Discount'], bins=[0, 10, 20, 30, 40, 50, 100], labels=['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50%+'])
discount_counts = discount_bins.value_counts().sort_index()

fig3 = px.pie(values=discount_counts, names=discount_counts.index, title="Distribution of Products by Discount Levels")
st.plotly_chart(fig3)

# 4. Bar Chart: Price Distribution by Range
st.header("Price Distribution")
# Define price ranges for bar chart
price_bins = pd.cut(data['Current Price'], bins=[0, 1000, 5000, 10000, 20000, 50000, data['Current Price'].max()],
                    labels=['<1000', '1000-5000', '5000-10000', '10000-20000', '20000-50000', '50000+'])
price_counts = price_bins.value_counts().sort_index()

fig4 = go.Figure(data=[go.Bar(
    x=price_counts.index.astype(str),
    y=price_counts,
    text=price_counts,
    textposition='auto'
)])
fig4.update_layout(title_text="Price Distribution by Range", xaxis_title="Price Range", yaxis_title="Number of Products")
st.plotly_chart(fig4)

# Display raw data
st.header("Raw Data")
if st.checkbox("Show Raw Data"):
    st.write(data)

# Summary Insights
st.subheader("Report: Pricing Trends & Best Times to Buy")
st.write("""
- **Top Discounts**: Displays the top 10 products with the highest current discounts, useful for identifying the best deals.
- **Product Distribution by Ratings**: Shows the distribution of products across different rating levels.
- **Discount Distribution**: Visualizes how discounts are distributed across products, highlighting the most common discount levels.
- **Price Distribution**: Groups products by price ranges to help understand the general price levels on the platform.
""")
