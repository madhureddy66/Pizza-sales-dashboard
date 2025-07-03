import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ------------------------------
# Step 1: Load your dataset
# ------------------------------
# Replace this with your actual CSV or database import
# Example:
# df = pd.read_csv('pizza_sales.csv')

# Simulated dataset for demo purposes
df = pd.DataFrame({
    'order_id': [1, 2, 3, 4, 5, 6, 7],
    'order_date': [
        '2023-01-15', '2023-02-10', '2023-02-25',
        '2023-03-05', '2023-03-15', '2023-04-01', '2023-04-20'
    ]
})

# ------------------------------
# Step 2: Convert order_date to datetime and extract month
# ------------------------------
df['order_date'] = pd.to_datetime(df['order_date'])
df['month_name'] = df['order_date'].dt.strftime('%B')

# ------------------------------
# Step 3: Group by month to get total orders
# ------------------------------
monthly_orders = df.groupby('month_name').agg(Total_Orders=('order_id', 'count')).reset_index()

# ------------------------------
# Step 4: Order the months correctly
# ------------------------------
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

monthly_orders['month_name'] = pd.Categorical(
    monthly_orders['month_name'],
    categories=month_order,
    ordered=True
)

monthly_orders = monthly_orders.sort_values('month_name')

# ------------------------------
# Step 5: Plotting
# ------------------------------
plt.figure(figsize=(10, 6))
sns.set(style="whitegrid")
ax = sns.lineplot(
    x='month_name',
    y='Total_Orders',
    data=monthly_orders,
    marker='o'
)

ax.set_xlabel('Month')
ax.set_ylabel('Total Orders')
ax.set_title('Monthly Total Orders')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()




   







