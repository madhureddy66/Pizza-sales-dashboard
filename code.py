import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Sample placeholder for loading data
# Replace this with your actual data loading method
# monthly_orders = pd.read_csv('monthly_orders.csv')  # or any DataFrame you are using

# Example for context
# Let's say monthly_orders looks like this:
# monthly_orders = pd.DataFrame({
#     'month_name': ['January', 'February', 'March', 'April'],
#     'Total_Orders': [150, 200, 180, 220]
# })

# Ensure the data exists
if 'monthly_orders' not in locals():
    st.error("monthly_orders DataFrame not found. Please load your data.")
else:
    # Debugging checks
    st.subheader("Debugging Information:")
    st.write("Data preview:")
    st.write(monthly_orders.head())
    st.write("Column names:", monthly_orders.columns.tolist())
    st.write("Data types:", monthly_orders.dtypes)
    st.write("Missing values:")
    st.write(monthly_orders[['month_name', 'Total_Orders']].isnull().sum())
    st.write("Is DataFrame empty?", monthly_orders.empty)

    # Drop missing values just in case
    monthly_orders = monthly_orders.dropna(subset=['month_name', 'Total_Orders'])

    # Convert Total_Orders to numeric in case it's not
    monthly_orders['Total_Orders'] = pd.to_numeric(monthly_orders['Total_Orders'], errors='coerce')

    # Create figure and axis
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Sort month names if needed (optional step)
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_orders['month_name'] = pd.Categorical(monthly_orders['month_name'], categories=month_order, ordered=True)
    monthly_orders = monthly_orders.sort_values('month_name')

    # Create the line plot
    sns.lineplot(x='month_name', y='Total_Orders', data=monthly_orders, marker='o', ax=ax1)
    ax1.set_title("Total Orders per Month")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Total Orders")
    plt.xticks(rotation=45)

    # Display in Streamlit
    st.pyplot(fig)


   







