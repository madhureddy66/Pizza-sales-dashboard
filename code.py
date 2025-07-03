import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- 1. Load and Inspect the Data ---
# IMPORTANT: Ensure 'Data Model - Pizza Sales.xlsx - pizza_sales.csv' is in the same
# directory as this Python script, or update the path below to its correct location.
try:
    df = pd.read_csv('Data Model - Pizza Sales.xlsx - pizza_sales.csv')
    print("CSV loaded successfully.")
except FileNotFoundError:
    print("Error: 'Data Model - Pizza Sales.xlsx - pizza_sales.csv' not found.")
    print("Please ensure the file is in the same directory or provide the full path.")
    exit()

# Data Preprocessing
# Convert 'order_date' to datetime objects
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce') # coerce invalid dates to NaT

# Ensure 'total_price' is numeric
df['total_price'] = pd.to_numeric(df['total_price'], errors='coerce')

# Drop rows with NaT in 'order_date' or NaN in 'total_price' after conversion
df.dropna(subset=['order_date', 'total_price'], inplace=True)

# --- DEBUGGING STEP 1: Check DataFrame after initial cleaning ---
print("\n--- Debugging: DataFrame after initial cleaning ---")
print(f"Is DataFrame empty? {df.empty}")
if not df.empty:
    print("First 5 rows of DataFrame:")
    print(df.head())
    print("\nDataFrame Info:")
    df.info()
else:
    print("DataFrame is empty after dropping NA values. Please check your CSV data or cleaning steps.")
    exit() # Exit if DataFrame is empty to prevent further errors

# Extract hour from order_time (assuming order_time is in a suitable format, e.g., "HH:MM:SS")
# If order_time is just time string, convert it to datetime and then extract hour.
# If it's already part of a datetime column, it's simpler. Assuming it's a string like "HH:MM:SS"
df['order_hour'] = pd.to_datetime(df['order_time'], errors='coerce').dt.hour
df.dropna(subset=['order_hour'], inplace=True)
df['order_hour'] = df['order_hour'].astype(int)


# --- 2. Perform Calculations Based on SQL Queries and Dashboard Elements ---

# Key Performance Indicators (KPIs)
total_revenue = df['total_price'].sum()
total_orders = df['order_id'].nunique()
average_order_value = total_revenue / total_orders if total_orders > 0 else 0
total_pizzas_sold = df['quantity'].sum()

print("\n--- Key Performance Indicators (KPIs) ---")
print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Total Orders: {total_orders:,}")
print(f"Average Order Value: ${average_order_value:,.2f}")
print(f"Total Pizzas Sold: {total_pizzas_sold:,}")


# Q7. Monthly Trend for Orders
df['month_name'] = df['order_date'].dt.month_name()
monthly_orders = df.groupby('month_name')['order_id'].nunique().reset_index()
# Order months chronologically for better visualization
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_orders['month_name'] = pd.Categorical(monthly_orders['month_name'], categories=month_order, ordered=True)
monthly_orders = monthly_orders.sort_values('month_name')

# --- DEBUGGING STEP 2: Check monthly_orders DataFrame before plotting ---
print("\n--- Debugging: monthly_orders DataFrame ---")
print(f"Is monthly_orders DataFrame empty? {monthly_orders.empty}")
if not monthly_orders.empty:
    print("First 5 rows of monthly_orders:")
    print(monthly_orders.head())
    print("\nmonthly_orders Info:")
    monthly_orders.info()
else:
    print("monthly_orders DataFrame is empty. This is likely the cause of the ValueError.")
    print("Please ensure 'order_date' column has valid dates and 'order_id' has unique values in your CSV.")
    exit() # Exit if monthly_orders is empty


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
sales_by_size = sales_by_size.sort_values('pizza_size').dropna() # Drop any NaN introduced by size_order if not all sizes are present


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
# The 'order_hour' column is already created and cleaned above
hourly_orders = df.groupby('order_hour')['order_id'].nunique().reset_index()
hourly_orders.columns = ['Order_Hour', 'Total_Orders']


# --- 3. Generate Visualizations (Dashboard Layout) ---

# Set a style for the plots
plt.style.use('ggplot')

# Create a figure and a grid of subplots for the dashboard
# Adjust figsize as needed to make plots readable
fig = plt.figure(figsize=(20, 25))
gs = fig.add_gridspec(5, 2, height_ratios=[0.1, 1, 1, 1, 1]) # 5 rows, 2 columns, adjust height ratios

# Add a placeholder for KPIs (text summary) at the top
ax_kpis = fig.add_subplot(gs[0, :])
ax_kpis.text(0.5, 0.5,
             f'Total Revenue: ${total_revenue:,.2f} | Total Orders: {total_orders:,} | '
             f'Avg. Order Value: ${average_order_value:,.2f} | Total Pizzas Sold: {total_pizzas_sold:,}',
             horizontalalignment='center', verticalalignment='center',
             fontsize=16, color='darkblue', transform=ax_kpis.transAxes)
ax_kpis.set_axis_off() # Hide axes for this text plot

# Plot 1: Monthly Trend for Orders (Line Chart)
ax1 = fig.add_subplot(gs[1, 0])
sns.lineplot(x='month_name', y='Total_Orders', data=monthly_orders, marker='o', ax=ax1)
ax1.set_title('Monthly Trend for Total Orders')
ax1.set_xlabel('Month')
ax1.set_ylabel('Total Orders')
ax1.grid(True)
ax1.tick_params(axis='x', rotation=45)

# Plot 2: % of Sales by Pizza Category (Donut Chart)
ax2 = fig.add_subplot(gs[1, 1])
wedgeprops = {'width': 0.3, 'edgecolor': 'white'}
colors = sns.color_palette('pastel')[0:len(sales_by_category)]
ax2.pie(sales_by_category['PCT'], labels=sales_by_category['pizza_category'], autopct='%1.1f%%',
        startangle=90, pctdistance=0.85, wedgeprops=wedgeprops, colors=colors)
centre_circle = plt.Circle((0,0), 0.70, fc='white')
ax2.add_artist(centre_circle)
ax2.set_title('% of Sales by Pizza Category')
ax2.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.

# Plot 3: Sales by Pizza Size (Pie Chart)
ax3 = fig.add_subplot(gs[2, 0])
colors = sns.color_palette('viridis')[0:len(sales_by_size)]
ax3.pie(sales_by_size['PCT'], labels=sales_by_size['pizza_size'], autopct='%1.1f%%', startangle=90, colors=colors)
ax3.set_title('% of Sales by Pizza Size')
ax3.axis('equal')

# Plot 4: Daily Trend for Total Orders (Line Chart)
ax4 = fig.add_subplot(gs[2, 1])
sns.lineplot(x='Order_Date', y='Total_Orders', data=daily_orders, marker='o', ax=ax4)
ax4.set_title('Daily Trend for Total Orders')
ax4.set_xlabel('Date')
ax4.set_ylabel('Total Orders')
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True)

# Plot 5: Hourly Trend for Total Orders (Bar Chart)
ax5 = fig.add_subplot(gs[3, 0])
sns.barplot(x='Order_Hour', y='Total_Orders', data=hourly_orders, palette='viridis', ax=ax5)
ax5.set_title('Hourly Trend for Total Orders')
ax5.set_xlabel('Hour of Day')
ax5.set_ylabel('Total Orders')
ax5.grid(axis='y')

# Plot 6: Top 5 Best Sellers by Revenue (Bar Chart)
ax6 = fig.add_subplot(gs[3, 1])
sns.barplot(x='total_price', y='pizza_name', data=top_5_revenue, palette='mako', ax=ax6)
ax6.set_title('Top 5 Best Sellers by Revenue')
ax6.set_xlabel('Total Revenue ($)')
ax6.set_ylabel('Pizza Name')

# Plot 7: Bottom 5 Best Sellers by Revenue (Bar Chart)
ax7 = fig.add_subplot(gs[4, 0])
sns.barplot(x='total_price', y='pizza_name', data=bottom_5_revenue, palette='mako_r', ax=ax7) # reversed palette
ax7.set_title('Bottom 5 Best Sellers by Revenue')
ax7.set_xlabel('Total Revenue ($)')
ax7.set_ylabel('Pizza Name')

# Plot 8: Top 5 Best Sellers by Quantity (Bar Chart)
ax8 = fig.add_subplot(gs[4, 1])
sns.barplot(x='quantity', y='pizza_name', data=top_5_quantity, palette='rocket', ax=ax8)
ax8.set_title('Top 5 Best Sellers by Quantity')
ax8.set_xlabel('Total Quantity Sold')
ax8.set_ylabel('Pizza Name')

# Note: Bottom 5 by Quantity calculation is present but not explicitly plotted in the current grid
# to keep the dashboard layout manageable. You can add it similarly if needed.

plt.tight_layout(rect=[0, 0.03, 1, 0.98]) # Adjust layout to make space for the overall title
plt.suptitle('Pizza Sales Dashboard', y=1.00, fontsize=20, weight='bold')
plt.show()
   







