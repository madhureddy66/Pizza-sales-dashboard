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
    df.dropna(subset=['order_date', 'total_price'], inplace=True)
    if df.empty:
        st.error("DataFrame is empty after cleaning 'order_date' and 'total_price'. Please check your CSV data.")
        st.stop()

    # Extract hour from order_time (assuming order_time is in a suitable format, e.g., "HH:MM:SS")
    df['order_hour'] = pd.to_datetime(df['order_time'], errors='coerce').dt.hour
    df.dropna(subset=['order_hour'], inplace=True)
    df['order_hour'] = df['order_hour'].astype(int)

    # Extract day of week
    df['day_of_week'] = df['order_date'].dt.day_name()
    df['month_name'] = df['order_date'].dt.month_name()

    if df.empty:
        st.error("DataFrame became empty after processing 'order_hour' or 'day_of_week'. Please check your data.")
        st.stop()

    # --- New Filters ---
    st.sidebar.header("Apply Filters")

    # Filter by Month
    all_months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
    selected_months = st.sidebar.multiselect("Select Month(s)", all_months, default=all_months)

    # Filter by Day of Week
    all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    selected_days = st.sidebar.multiselect("Select Day(s) of Week", all_days, default=all_days)

    # Filter by Hour of Day
    all_hours = sorted(df['order_hour'].unique().tolist())
    selected_hours = st.sidebar.multiselect("Select Hour(s) of Day", all_hours, default=all_hours)

    # Filter by Pizza Category
    all_categories = df['pizza_category'].unique().tolist()
    selected_categories = st.sidebar.multiselect("Select Pizza Category(ies)", all_categories, default=all_categories)

    # Filter by Pizza Size
    all_sizes = df['pizza_size'].unique().tolist()
    # Ensure consistent order for sizes if not all present
    size_order_filter = ['S', 'M', 'L', 'XL', 'XXL']
    all_sizes_ordered = [s for s in size_order_filter if s in all_sizes]
    selected_sizes = st.sidebar.multiselect("Select Pizza Size(s)", all_sizes_ordered, default=all_sizes_ordered)


    # Apply filters to the DataFrame
    filtered_df = df[
        (df['month_name'].isin(selected_months)) &
        (df['day_of_week'].isin(selected_days)) &
        (df['order_hour'].isin(selected_hours)) &
        (df['pizza_category'].isin(selected_categories)) &
        (df['pizza_size'].isin(selected_sizes))
    ].copy() # Use .copy() to avoid SettingWithCopyWarning

    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your selections.")
        st.stop()

    # --- 2. Perform Calculations Based on SQL Queries and Dashboard Elements ---

    st.subheader("Key Performance Indicators (KPIs)")

    # Key Performance Indicators (KPIs)
    total_revenue = filtered_df['total_price'].sum()
    total_orders = filtered_df['order_id'].nunique()
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0
    total_pizzas_sold = filtered_df['quantity'].sum()

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
    monthly_orders = filtered_df.groupby('month_name')['order_id'].nunique().reset_index(name='Total_Orders')
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_orders['month_name'] = pd.Categorical(monthly_orders['month_name'], categories=month_order, ordered=True)
    monthly_orders = monthly_orders.sort_values('month_name')

    if monthly_orders.empty:
        st.warning("Monthly orders data is empty based on current filters. Cannot generate monthly trend plot.")
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
        plt.close(fig1)

    # Q8. % of Sales by Pizza Category
    sales_by_category = filtered_df.groupby('pizza_category')['total_price'].sum().reset_index()
    sales_by_category['PCT'] = (sales_by_category['total_price'] / total_revenue * 100).round(2) if total_revenue > 0 else 0
    sales_by_category.rename(columns={'total_price': 'Total_Revenue'}, inplace=True)

    # Sales by Pizza Size
    sales_by_size = filtered_df.groupby('pizza_size')['total_price'].sum().reset_index()
    sales_by_size['PCT'] = (sales_by_size['total_price'] / total_revenue * 100).round(2) if total_revenue > 0 else 0
    sales_by_size.rename(columns={'total_price': 'Total_Revenue'}, inplace=True)
    size_order = ['S', 'M', 'L', 'XL', 'XXL']
    sales_by_size['pizza_size'] = pd.Categorical(sales_by_size['pizza_size'], categories=size_order, ordered=True)
    sales_by_size = sales_by_size.sort_values('pizza_size').dropna()


    # Top 5 Best Sellers by Revenue and Quantity
    top_5_revenue = filtered_df.groupby('pizza_name')['total_price'].sum().nlargest(5).reset_index()
    top_5_quantity = filtered_df.groupby('pizza_name')['quantity'].sum().nlargest(5).reset_index()

    # Bottom 5 Best Sellers by Revenue and Quantity
    bottom_5_revenue = filtered_df.groupby('pizza_name')['total_price'].sum().nsmallest(5).reset_index()
    bottom_5_quantity = filtered_df.groupby('pizza_name')['quantity'].sum().nsmallest(5).reset_index()

    # Daily Trend for Total Orders
    daily_orders = filtered_df.groupby(filtered_df['order_date'].dt.date)['order_id'].nunique().reset_index()
    daily_orders.columns = ['Order_Date', 'Total_Orders']
    daily_orders['Order_Date'] = pd.to_datetime(daily_orders['Order_Date'])


    # Hourly Trend for Total Orders
    hourly_orders = filtered_df.groupby('order_hour')['order_id'].nunique().reset_index()
    hourly_orders.columns = ['Order_Hour', 'Total_Orders']


    # --- 3. Generate Visualizations (Dashboard Layout) ---

    st.markdown("---")

    # Row 1 of plots
    col_plot1, col_plot2 = st.columns(2)

    with col_plot1:
        st.subheader("% of Sales by Pizza Category")
        if sales_by_category.empty or sales_by_category['PCT'].sum() == 0:
            st.warning("No sales by category data based on current filters.")
        else:
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
        if sales_by_size.empty or sales_by_size['PCT'].sum() == 0:
            st.warning("No sales by size data based on current filters.")
        else:
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
        if daily_orders.empty:
            st.warning("No daily orders data based on current filters.")
        else:
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
        if hourly_orders.empty:
            st.warning("No hourly orders data based on current filters.")
        else:
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
        if top_5_revenue.empty:
            st.warning("No top sellers by revenue data based on current filters.")
        else:
            fig6, ax6 = plt.subplots(figsize=(10, 6))
            sns.barplot(x='total_price', y='pizza_name', data=top_5_revenue, palette='mako', ax=ax6)
            ax6.set_title('Top 5 Best Sellers by Revenue')
            ax6.set_xlabel('Total Revenue ($)')
            ax6.set_ylabel('Pizza Name')
            st.pyplot(fig6)
            plt.close(fig6)

    with col_plot6:
        st.subheader("Bottom 5 Best Sellers by Revenue")
        if bottom_5_revenue.empty:
            st.warning("No bottom sellers by revenue data based on current filters.")
        else:
            fig7, ax7 = plt.subplots(figsize=(10, 6))
            sns.barplot(x='total_price', y='pizza_name', data=bottom_5_revenue, palette='mako_r', ax=ax7) # reversed palette
            ax7.set_title('Bottom 5 Best Sellers by Revenue')
            ax7.set_xlabel('Total Revenue ($)')
            ax7.set_ylabel('Pizza Name')
            st.pyplot(fig7)
            plt.close(fig7)

    st.markdown("---")

    # Row 4 (Adding new plot here)
    col_plot7, col_plot8 = st.columns(2)

    with col_plot7:
        st.subheader("Top 5 Best Sellers by Quantity")
        if top_5_quantity.empty:
            st.warning("No top sellers by quantity data based on current filters.")
        else:
            fig8, ax8 = plt.subplots(figsize=(10, 6))
            sns.barplot(x='quantity', y='pizza_name', data=top_5_quantity, palette='rocket', ax=ax8)
            ax8.set_title('Top 5 Best Sellers by Quantity')
            ax8.set_xlabel('Total Quantity Sold')
            ax8.set_ylabel('Pizza Name')
            st.pyplot(fig8)
            plt.close(fig8)

    with col_plot8:
        st.subheader("Daily Orders Trend by Pizza Category")
        daily_category_orders = filtered_df.groupby([filtered_df['order_date'].dt.date, 'pizza_category'])['order_id'].nunique().reset_index()
        daily_category_orders.columns = ['Order_Date', 'Pizza_Category', 'Total_Orders']
        daily_category_orders['Order_Date'] = pd.to_datetime(daily_category_orders['Order_Date'])

        if daily_category_orders.empty:
            st.warning("No daily orders by category data based on current filters.")
        else:
            fig9, ax9 = plt.subplots(figsize=(10, 6))
            sns.lineplot(x='Order_Date', y='Total_Orders', hue='Pizza_Category', data=daily_category_orders, marker='o', ax=ax9)
            ax9.set_title('Daily Orders Trend by Pizza Category')
            ax9.set_xlabel('Date')
            ax9.set_ylabel('Total Orders')
            ax9.tick_params(axis='x', rotation=45)
            ax9.legend(title='Pizza Category', bbox_to_anchor=(1.05, 1), loc='upper left')
            ax9.grid(True)
            plt.tight_layout()
            st.pyplot(fig9)
            plt.close(fig9)

    st.markdown("---")
    st.header("💡 Strategies to Boost Pizza Sales")
    st.write("Based on the data and common business practices, here are some actionable suggestions:")

    with st.expander("🚀 Promote Best Sellers & Address Underperformers"):
        st.markdown("""
        * **Feature Top-Selling Pizzas:**
            * Run limited-time promotions (e.g., "Buy one 'The Classic Deluxe', get 20% off 'The Barbecue Chicken Pizza'").
            * Create combo deals that include top performers (e.g., "Family Feast: 2 'The Pepperoni Pizza' + Sides").
            * Highlight them prominently on your menu and marketing materials.
        * **Revitalize Bottom-Selling Pizzas:**
            * Analyze if their ingredients are unpopular or if they are priced too high.
            * Introduce "Chef's Special" versions with new twists or limited-time ingredient swaps.
            * Offer them as a low-cost add-on or sample with larger orders.
            * Consider temporary price reductions to increase trial.
        """)

    with st.expander("⏰ Optimize for Hourly & Daily Trends"):
        st.markdown("""
        * **Boost Off-Peak Hours:**
            * Implement "Happy Hour" deals (e.g., discounts on selected pizzas/drinks) during slower times (e.g., 2 PM - 5 PM).
            * Offer delivery-only specials during lunch lulls.
            * Run online-exclusive promotions for slower hours.
        * **Maximize Peak Hours:**
            * Ensure adequate staffing during busiest periods (e.g., 6 PM - 9 PM) to maintain quick service and customer satisfaction.
            * Streamline order processing and delivery logistics to handle high volume.
            * Consider premium pricing for certain items during peak demand if customer tolerance allows.
        * **Target Specific Days:**
            * If weekends are dominant, focus marketing efforts on building weekday sales with unique promotions (e.g., "Tuesday Two-for-One").
            * Analyze specific weekday lulls for targeted promotions.
        """)

    with st.expander("📊 Leverage Category & Size Insights"):
        st.markdown("""
        * **Category-Specific Campaigns:**
            * If 'Veggie' pizzas are popular, launch a "Meatless Monday" promotion or a "Build Your Own Veggie" special.
            * If 'Chicken' pizzas are doing well, introduce new chicken-based pizza variations.
        * **Size-Based Deals:**
            * Since 'Large' pizzas often dominate, create family meal bundles centered around large pizzas.
            * Promote smaller sizes for individual diners or as a lunch special.
            * Consider introducing new sizes if there's a market gap (e.g., a mini-pizza for kids).
        """)

    with st.expander("🗓️ Strategic Monthly Promotions"):
        st.markdown("""
        * **Boost Slower Months:**
            * Identify historically slower months (e.g., September, December, based on the monthly trend) and plan aggressive marketing campaigns or new menu launches for those periods.
            * Offer seasonal pizzas or limited-time flavors that align with holidays or seasonal ingredients.
        * **Reinforce Peak Months:**
            * Capitalize on peak months by offering loyalty bonuses or exclusive deals for repeat customers to maintain momentum.
            * Launch new, high-value premium pizzas.
        """)

    st.sidebar.markdown("---")
    st.sidebar.info("Dashboard created using Streamlit, Pandas, Matplotlib, and Seaborn.")






   







