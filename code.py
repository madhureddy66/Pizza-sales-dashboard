import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Pizza Sales Dashboard")

st.title("🍕 Pizza Sales Dashboard")

# --- 1. File Uploader ---
st.sidebar.header("Upload your Data")
uploaded_file = st.sidebar.file_uploader("Choose your 'pizza_sales.csv' file", type="csv")

df = None # Initialize df outside the if block

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("CSV loaded successfully!")
    except Exception as e:
        st.error(f"Error loading CSV file: {e}. Please ensure it's a valid CSV.")
        st.stop() # Stop execution if file cannot be read
else:
    st.info("Please upload a CSV file to view the dashboard.")
    st.stop() # Stop execution if no file is uploaded

# --- Data Preprocessing ---
if df is not None:
    # Convert 'order_date' to datetime objects
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce') # coerce invalid dates to NaT

    # Ensure 'total_price' is numeric
    df['total_price'] = pd.to_numeric(df['total_price'], errors='coerce')

    # Drop rows with NaT in 'order_date' or NaN in 'total_price' after conversion
    initial_rows = df.shape[0]
    df.dropna(subset=['order_date', 'total_price'], inplace=True)
    if df.empty:
        st.error("DataFrame is empty after cleaning 'order_date' and 'total_price'. Please check your CSV data.")
        st.stop()

    # Extract hour from order_time (assuming order_time is in a suitable format, e.g., "HH:MM:SS")
    df['order_hour'] = pd.to_datetime(df['order_time'], errors='coerce').dt.hour
    df.dropna(subset=['order_hour'], inplace=True)
    df['order_hour'] = df['order_hour'].astype(int)
    if df.empty:
        st.error("DataFrame became empty after processing 'order_hour'. Please check your 'order_time' column.")
        st.stop()


    # --- 2. Perform Calculations Based on SQL Queries and Dashboard Elements ---

    st.subheader("Key Performance Indicators (KPIs)")

    # Key Performance Indicators (KPIs)
    total_revenue = df['total_price'].sum()
    total_orders = df['order_id'].nunique()
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0
    total_pizzas_sold = df['quantity'].sum()

    # Display KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col2:
        st.metric("Total Orders", f"{total_orders:,}")
    with col3:
        st.metric("Average Order Value", f"${average_order_value:,.2f}")
    with col4:
        st.metric("Total Pizzas Sold", f"{total_pizzas_sold:,}")

    # Q7. Monthly Trend for Orders
    df['month_name'] = df['order_date'].dt.month_name()
    monthly_orders = df.groupby('month_name')['order_id'].nunique().reset_index(name='Total_Orders') # Renamed column
    # Order months chronologically for better visualization
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_orders['month_name'] = pd.Categorical(monthly_orders['month_name'], categories=month_order, ordered=True)
    monthly_orders = monthly_orders.sort_values('month_name')

    if monthly_orders.empty:
        st.warning("Monthly orders data is empty. Cannot generate monthly trend plot.")
    else:
        st.markdown("---")
        st.subheader("Monthly Trend for Orders")
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='month_name', y='Total_Orders', data=monthly_orders, marker='o', ax=ax1)
        ax1.set_title('Monthly Trend for Total Orders')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Total Orders')
        ax1.grid(True)
        ax1.tick_params(axis='x', rotation=45)
        st.pyplot(fig1)
        plt.close(fig1) # Close the figure to prevent display issues in Streamlit

    # Q8. % of Sales by Pizza Category
    sales_by_category = df.groupby('pizza_category')['total_price'].sum().reset_index()
    sales_by_category['PCT'] = (sales_by_category['total_price'] / total_revenue * 100).round(2)
    sales_by_category.rename(columns={'total_price': 'Total_Revenue'}, inplace=True)

    # Sales by Pizza Size
    sales_by_size = df.groupby('pizza_size')['total_price'].sum().reset_index()
    sales_by_size['PCT'] = (sales_by_size['total_price'] / total_revenue * 100).round(2)
    sales_by_size.rename(columns={'total_price': 'Total_Revenue'}, inplace=True)
    # Order sizes for better visualization (if specific order is desired)
    size_order = ['S', 'M', 'L', 'XL', 'XXL'] # Assuming S, M, L, XL, XXL are the sizes
    sales_by_size['pizza_size'] = pd.Categorical(sales_by_size['pizza_size'], categories=size_order, ordered=True)
    sales_by_size = sales_by_size.sort_values('pizza_size').dropna()


    # Top 5 Best Sellers by Revenue and Quantity
    top_5_revenue = df.groupby('pizza_name')['total_price'].sum().nlargest(5).reset_index()
    top_5_quantity = df.groupby('pizza_name')['quantity'].sum().nlargest(5).reset_index()

    # Bottom 5 Best Sellers by Revenue and Quantity
    bottom_5_revenue = df.groupby('pizza_name')['total_price'].sum().nsmallest(5).reset_index()
    bottom_5_quantity = df.groupby('pizza_name')['quantity'].sum().nsmallest(5).reset_index()

    # Daily Trend for Total Orders
    daily_orders = df.groupby(df['order_date'].dt.date)['order_id'].nunique().reset_index()
    daily_orders.columns = ['Order_Date', 'Total_Orders']
    daily_orders['Order_Date'] = pd.to_datetime(daily_orders['Order_Date']) # Convert back to datetime for plotting


    # Hourly Trend for Total Orders
    hourly_orders = df.groupby('order_hour')['order_id'].nunique().reset_index()
    hourly_orders.columns = ['Order_Hour', 'Total_Orders']


    # --- 3. Generate Visualizations (Dashboard Layout) ---

    st.markdown("---")

    # Row 1 of plots
    col_plot1, col_plot2 = st.columns(2)

    with col_plot1:
        st.subheader("% of Sales by Pizza Category")
        fig2, ax2 = plt.subplots(figsize=(8, 8))
        wedgeprops = {'width': 0.3, 'edgecolor': 'white'}
        colors = sns.color_palette('pastel')[0:len(sales_by_category)]
        ax2.pie(sales_by_category['PCT'], labels=sales_by_category['pizza_category'], autopct='%1.1f%%',
                startangle=90, pctdistance=0.85, wedgeprops=wedgeprops, colors=colors)
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        ax2.add_artist(centre_circle)
        ax2.set_title('% of Sales by Pizza Category')
        ax2.axis('equal')
        st.pyplot(fig2)
        plt.close(fig2)

    with col_plot2:
        st.subheader("Sales by Pizza Size")
        fig3, ax3 = plt.subplots(figsize=(8, 8))
        colors = sns.color_palette('viridis')[0:len(sales_by_size)]
        ax3.pie(sales_by_size['PCT'], labels=sales_by_size['pizza_size'], autopct='%1.1f%%', startangle=90, colors=colors)
        ax3.set_title('% of Sales by Pizza Size')
        ax3.axis('equal')
        st.pyplot(fig3)
        plt.close(fig3)

    st.markdown("---")

    # Row 2 of plots
    col_plot3, col_plot4 = st.columns(2)

    with col_plot3:
        st.subheader("Daily Trend for Total Orders")
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='Order_Date', y='Total_Orders', data=daily_orders, marker='o', ax=ax4)
        ax4.set_title('Daily Trend for Total Orders')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Total Orders')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True)
        st.pyplot(fig4)
        plt.close(fig4)

    with col_plot4:
        st.subheader("Hourly Trend for Total Orders")
        fig5, ax5 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Order_Hour', y='Total_Orders', data=hourly_orders, palette='viridis', ax=ax5)
        ax5.set_title('Hourly Trend for Total Orders')
        ax5.set_xlabel('Hour of Day')
        ax5.set_ylabel('Total Orders')
        ax5.grid(axis='y')
        st.pyplot(fig5)
        plt.close(fig5)

    st.markdown("---")

    # Row 3 of plots
    col_plot5, col_plot6 = st.columns(2)

    with col_plot5:
        st.subheader("Top 5 Best Sellers by Revenue")
        fig6, ax6 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='total_price', y='pizza_name', data=top_5_revenue, palette='mako', ax=ax6)
        ax6.set_title('Top 5 Best Sellers by Revenue')
        ax6.set_xlabel('Total Revenue ($)')
        ax6.set_ylabel('Pizza Name')
        st.pyplot(fig6)
        plt.close(fig6)

    with col_plot6:
        st.subheader("Bottom 5 Best Sellers by Revenue")
        fig7, ax7 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='total_price', y='pizza_name', data=bottom_5_revenue, palette='mako_r', ax=ax7) # reversed palette
        ax7.set_title('Bottom 5 Best Sellers by Revenue')
        ax7.set_xlabel('Total Revenue ($)')
        ax7.set_ylabel('Pizza Name')
        st.pyplot(fig7)
        plt.close(fig7)

    st.markdown("---")

    # Row 4 (Optional, if you want to add Bottom 5 by Quantity)
    col_plot7, col_plot8 = st.columns(2)

    with col_plot7:
        st.subheader("Top 5 Best Sellers by Quantity")
        fig8, ax8 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='quantity', y='pizza_name', data=top_5_quantity, palette='rocket', ax=ax8)
        ax8.set_title('Top 5 Best Sellers by Quantity')
        ax8.set_xlabel('Total Quantity Sold')
        ax8.set_ylabel('Pizza Name')
        st.pyplot(fig8)
        plt.close(fig8)

    # You could add bottom 5 quantity here in col_plot8 if desired.
    # For now, leaving it empty or adding some text.
    with col_plot8:
        st.write("More insights can be added here!")

    st.sidebar.markdown("---")
    st.sidebar.info("Dashboard created using Streamlit, Pandas, Matplotlib, and Seaborn.")






   







