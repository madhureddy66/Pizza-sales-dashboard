import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Sample DataFrame creation (Replace this with your actual monthly_orders DataFrame)
# monthly_orders = pd.read_csv("your_csv_file.csv")  # Example if you're loading from a file

# Assuming 'monthly_orders' is already defined earlier in your app
# Step 1: Check if required columns exist
required_columns = ['month_name', 'Total_Orders']
if not all(col in monthly_orders.columns for col in required_columns):
    raise ValueError(f"DataFrame must contain columns: {required_columns}")

# Step 2: Drop rows with missing values in the required columns
monthly_orders = monthly_orders.dropna(subset=['month_name', 'Total_Orders'])

# Step 3: Ensure correct data types
monthly_orders['Total_Orders'] = pd.to_numeric(monthly_orders['Total_Orders'], errors='coerce')
monthly_orders = monthly_orders.dropna(subset=['Total_Orders'])

# Step 4: Ensure 'month_name' is in correct order for plotting
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

monthly_orders['month_name'] = pd.Categorical(
    monthly_orders['month_name'],
    categories=month_order,
    ordered=True
)

monthly_orders = monthly_orders.sort_values('month_name')

# Step 5: Plotting
plt.figure(figsize=(10, 6))
sns.set(style="whitegrid")
ax = sns.lineplot(x='month_name', y='Total_Orders', data=monthly_orders, marker='o')

# Optional: Add axis labels and title
ax.set_xlabel('Month')
ax.set_ylabel('Total Orders')
ax.set_title('Monthly Total Orders')

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)
plt.tight_layout()

# Show plot
plt.show()



   







