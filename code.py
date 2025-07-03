import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv("Data Model - Pizza Sales.xlsx - pizza_sales.csv")

# Convert 'order_date' and 'order_time' to proper datetime formats
df['order_date'] = pd.to_datetime(df['order_date'])
df['order_time'] = pd.to_datetime(df['order_time'], format='%H:%M:%S').dt.time

# Extract additional date and time-based features
df['hour'] = pd.to_datetime(df['order_time'], format='%H:%M:%S').dt.hour
df['day_of_week'] = df['order_date'].dt.day_name()
df['week_number'] = df['order_date'].dt.isocalendar().week
df['month'] = df['order_date'].dt.month_name()

# Calculate total price for each order line
df['total_price'] = df['unit_price'] * df['quantity']

# Summary statistics (optional display for validation)
total_revenue = df['total_price'].sum()
total_orders = df['order_id'].nunique()
total_pizzas_sold = df['quantity'].sum()
avg_order_value = df.groupby('order_id')['total_price'].sum().mean()
avg_pizzas_per_order = total_pizzas_sold / total_orders

# Print business KPIs
print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Average Order Value: ${avg_order_value:,.2f}")
print(f"Total Pizzas Sold: {total_pizzas_sold}")
print(f"Total Orders: {total_orders}")
print(f"Avg Pizzas per Order: {avg_pizzas_per_order:.2f}")

# Export the cleaned and enriched dataset for Tableau
df.to_csv("cleaned_pizza_sales.csv", index=False)






   







