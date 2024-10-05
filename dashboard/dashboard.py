import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import streamlit_folium
import os


# Function to load the data
def load_data(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, file_name)
    df = pd.read_csv(file_path)
    return df

# Load the data
all_data = load_data("all_data.csv")

# Create a Streamlit app
st.title("E-Commerce Dashboard")

# Navigation menu
st.sidebar.title("Navigation")
nav_options = ["Data", "RFM Analysis", "Geospatial Analysis", "Cluster Analysis", "About"]
nav_choice = st.sidebar.selectbox("Pilih opsi", nav_options)

# Data Summary
if nav_choice == "Data":
    st.header("Data")
    st.write("Here is a summary of the data contained in all_data.csv:")

    # Add search feature
    st.write("Data Search:")
    search_type = st.selectbox("Select search type:", ["Date", "Payment Methods", "City", "Country"])

    # Check if search_type is not None
    if search_type is not None:
        # Initialize filtered_data
        filtered_data = all_data  # default to all data if no search type is selected

        if search_type == "Date":
            start_date = st.date_input("Enter start date:")
            end_date = st.date_input("Enter end date:")
            all_data['order_purchase_timestamp'] = pd.to_datetime(all_data['order_purchase_timestamp'])
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            filtered_data = all_data[(all_data['order_purchase_timestamp'] >= start_date) & (all_data['order_purchase_timestamp'] <= end_date)]
        elif search_type == "Payment Methods":
            payment_method = st.selectbox("Select payment method:", all_data['payment_type'].unique())
            filtered_data = all_data[all_data['payment_type'] == payment_method]
        elif search_type == "City":
            city = st.selectbox("Select city:", all_data['customer_city'].unique())
            filtered_data = all_data[all_data['customer_city'] == city]
        elif search_type == "Country":
            country = st.selectbox("Select country:", all_data['customer_state'].unique())
            filtered_data = all_data[all_data['customer_state'] == country]

        # Show search results
        st.write("Hasil Pencarian:")
        st.write(filtered_data.head())
        st.write(filtered_data.info())
        st.write(filtered_data.describe())

# Analisis RFM
elif nav_choice == "RFM Analysis":
    st.header("RFM Analysis")
    st.write("Here is a geospatial analysis of the data in all_data.csv:")
    all_data['order_purchase_timestamp'] = pd.to_datetime(all_data['order_purchase_timestamp'])
    all_data['recency'] = (all_data['order_purchase_timestamp'].max() - all_data['order_purchase_timestamp']).dt.days
    all_data['frequency'] = all_data.groupby('customer_id')['order_id'].transform('count')
    all_data['monetary'] = all_data.groupby('customer_id')['price'].transform('sum')
    fig = go.Figure(data=[go.Scatter(x=all_data['recency'], y=all_data['frequency'], mode='markers', marker=dict(color=all_data['monetary']))])
    st.plotly_chart(fig)

# Analisis Geospasial
elif nav_choice == "Geospatial Analysis":
    st.header("Geospatial Analysis")
    st.write("Here is a geospatial analysis of the data in all_data.csv:")

    # Create a geopandas dataframe
    zip_code_coords = {
        '01000-000': (-23.5505, -46.6333),  # Sao Paulo
        '02000-000': (-22.9068, -43.1729),  # Rio de Janeiro

    }
    all_data['latitude'] = all_data['customer_zip_code_prefix'].apply(lambda x: zip_code_coords.get(x, (0, 0))[0])
    all_data['longitude'] = all_data['customer_zip_code_prefix'].apply(lambda x: zip_code_coords.get(x, (0, 0))[1])
    geo_data = gpd.GeoDataFrame(all_data, geometry=gpd.points_from_xy(all_data.longitude, all_data.latitude))

    # Create a Folium map
    m = folium.Map(location=[-20.5937, -54.6372], zoom_start=4)
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers to the map
    for index, row in geo_data.iterrows():
        folium.Marker(location=[row.geometry.x, row.geometry.y], popup=row.customer_city).add_to(marker_cluster)

    # Display the map
    st.write("Customer Location Map")
    streamlit_folium.st_folium(m, width=800, height=600)

# Cluster Analysis
elif nav_choice == "Cluster Analysis":
    st.header("Cluster Analysis")
    st.write("Here is a cluster analysis of the data in all_data.csv:")
    fig, ax = plt.subplots()
    sns.scatterplot(x=all_data['customer_zip_code_prefix'], y=all_data['price'], ax=ax)
    st.pyplot(fig)

# About
else:
    st.header("About")
    st.write("This dashboard is built using Streamlit and Python.")

st.caption('Copyright © Mohd. Yusri Nasrol 2024')
