"""
Create Power BI Dashboard Documentation and Mock Visualizations
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import os

# Set paths
BASE_PATH = "/home/ubuntu/dataengineer-transformations-python/finchmart_sales_etl"
EXPORT_PATH = f"{BASE_PATH}/data/gold/powerbi_export"
DOCS_PATH = f"{BASE_PATH}/docs"
POWERBI_PATH = f"{BASE_PATH}/powerbi"

# Create directories
os.makedirs(DOCS_PATH, exist_ok=True)
os.makedirs(POWERBI_PATH, exist_ok=True)

def load_data():
    """Load all exported CSV files"""
    print("Loading data from CSV exports...")
    
    daily_sales = pd.read_csv(f"{EXPORT_PATH}/daily_sales.csv")
    store_performance = pd.read_csv(f"{EXPORT_PATH}/store_performance.csv")
    top_products = pd.read_csv(f"{EXPORT_PATH}/top_products.csv")
    customer_spending = pd.read_csv(f"{EXPORT_PATH}/customer_spending.csv")
    transactions = pd.read_csv(f"{EXPORT_PATH}/transactions_detail.csv")
    
    print(f"✓ Daily sales: {len(daily_sales)} records")
    print(f"✓ Store performance: {len(store_performance)} records")
    print(f"✓ Top products: {len(top_products)} records")
    print(f"✓ Customer spending: {len(customer_spending)} records")
    print(f"✓ Transactions: {len(transactions)} records\n")
    
    return daily_sales, store_performance, top_products, customer_spending, transactions

def create_visualizations(daily_sales, store_performance, top_products, customer_spending):
    """Create mock visualizations similar to Power BI dashboard"""
    print("Creating visualization mockups...")
    
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Create a figure with 4 subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Sales Trend Over Time (Line Chart)
    ax1 = plt.subplot(2, 2, 1)
    daily_sales['transaction_date'] = pd.to_datetime(daily_sales['transaction_date'])
    ax1.plot(daily_sales['transaction_date'], daily_sales['total_sales'], 
             marker='o', linewidth=2, markersize=8, color='#1f77b4')
    ax1.set_title('Sales Trend Over Time', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Total Sales ($)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Store Performance (Bar Chart)
    ax2 = plt.subplot(2, 2, 2)
    store_totals = store_performance.groupby('store_location')['total_sales'].sum().sort_values(ascending=False)
    colors = plt.cm.viridis(range(len(store_totals)))
    ax2.barh(store_totals.index, store_totals.values, color=colors)
    ax2.set_title('Store Performance by Total Sales', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Total Sales ($)', fontsize=12)
    ax2.set_ylabel('Store Location', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='x')
    
    # 3. Top Products Sold (Bar Chart)
    ax3 = plt.subplot(2, 2, 3)
    top_5 = top_products.nlargest(5, 'total_revenue')
    colors = plt.cm.plasma(range(len(top_5)))
    ax3.bar(range(len(top_5)), top_5['total_revenue'], color=colors)
    ax3.set_title('Top 5 Products by Revenue', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Product', fontsize=12)
    ax3.set_ylabel('Total Revenue ($)', fontsize=12)
    ax3.set_xticks(range(len(top_5)))
    ax3.set_xticklabels([f"{p[:15]}..." if len(p) > 15 else p for p in top_5['product_name']], 
                        rotation=45, ha='right')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Customer Spending Behavior (Scatter Plot)
    ax4 = plt.subplot(2, 2, 4)
    scatter = ax4.scatter(customer_spending['transaction_count'], 
                         customer_spending['total_spent'],
                         c=customer_spending['avg_transaction_value'],
                         cmap='coolwarm', s=50, alpha=0.6)
    ax4.set_title('Customer Spending Behavior', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Number of Transactions', fontsize=12)
    ax4.set_ylabel('Total Spent ($)', fontsize=12)
    ax4.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax4, label='Avg Transaction Value ($)')
    
    plt.tight_layout()
    
    # Save the figure
    output_file = f"{POWERBI_PATH}/dashboard_mockup.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Dashboard mockup saved to: {output_file}\n")
    plt.close()
    
    return output_file

def create_powerbi_documentation():
    """Create Power BI dashboard documentation"""
    print("Creating Power BI documentation...")
    
    doc_content = """# Power BI Dashboard Documentation
## FinchMart Sales Analytics Dashboard

### Overview
This Power BI dashboard provides comprehensive insights into FinchMart's sales performance, enabling data-driven decision-making for business stakeholders.

### Data Sources
The dashboard connects to the following CSV files exported from the Gold layer:

1. **daily_sales.csv** - Daily aggregated sales metrics
2. **store_performance.csv** - Store-level performance by date
3. **top_products.csv** - Top 5 products by revenue per day
4. **customer_spending.csv** - Customer lifetime value and behavior
5. **transactions_detail.csv** - Detailed transaction-level data

### Dashboard Components

#### 1. Sales Trend Over Time (Line Chart)
**Purpose:** Visualize sales performance trends across time periods

**Data Source:** `daily_sales.csv`

**Key Metrics:**
- Total Sales (Y-axis)
- Transaction Date (X-axis)
- Transaction Count (Tooltip)
- Average Transaction Value (Tooltip)

**DAX Measures:**
```dax
Total Sales = SUM(daily_sales[total_sales])
Avg Transaction Value = AVERAGE(daily_sales[avg_transaction_value])
Sales Growth % = 
    VAR CurrentSales = [Total Sales]
    VAR PreviousSales = CALCULATE([Total Sales], DATEADD(daily_sales[transaction_date], -1, DAY))
    RETURN DIVIDE(CurrentSales - PreviousSales, PreviousSales, 0)
```

**Filters:** Date range slicer

---

#### 2. Store Performance (Bar Chart)
**Purpose:** Compare sales performance across different store locations

**Data Source:** `store_performance.csv`

**Key Metrics:**
- Store Location (Y-axis)
- Total Sales (X-axis)
- Transaction Count (Tooltip)
- Unique Customers (Tooltip)

**DAX Measures:**
```dax
Store Total Sales = 
    CALCULATE(
        SUM(store_performance[total_sales]),
        ALLEXCEPT(store_performance, store_performance[store_location])
    )

Store Rank = 
    RANKX(
        ALL(store_performance[store_location]),
        [Store Total Sales],
        ,
        DESC,
        DENSE
    )
```

**Filters:** Date range slicer, Store location slicer

---

#### 3. Top Products Sold (Table/Bar Chart)
**Purpose:** Identify best-selling products by revenue

**Data Source:** `top_products.csv`

**Key Metrics:**
- Product Name
- Product Category
- Total Revenue
- Total Quantity Sold
- Revenue Rank

**DAX Measures:**
```dax
Product Revenue = SUM(top_products[total_revenue])

Product Revenue % = 
    DIVIDE(
        [Product Revenue],
        CALCULATE([Product Revenue], ALL(top_products[product_name])),
        0
    )

Top 5 Products = 
    TOPN(
        5,
        VALUES(top_products[product_name]),
        [Product Revenue],
        DESC
    )
```

**Filters:** Date range slicer, Product category slicer

---

#### 4. Customer Spending Behavior (Scatter Plot / KPI Cards)
**Purpose:** Analyze customer lifetime value and purchasing patterns

**Data Source:** `customer_spending.csv`

**Key Metrics:**
- Total Spent (X-axis for scatter)
- Transaction Count (Y-axis for scatter)
- Average Transaction Value (Color/Size)
- Customer Segments

**DAX Measures:**
```dax
Customer Lifetime Value = SUM(customer_spending[total_spent])

Avg Customer Value = AVERAGE(customer_spending[total_spent])

High Value Customers = 
    CALCULATE(
        DISTINCTCOUNT(customer_spending[customer_id]),
        customer_spending[total_spent] > [Avg Customer Value]
    )

Customer Segment = 
    SWITCH(
        TRUE(),
        customer_spending[total_spent] >= 2000, "Premium",
        customer_spending[total_spent] >= 1000, "Gold",
        customer_spending[total_spent] >= 500, "Silver",
        "Bronze"
    )
```

**Filters:** Customer segment slicer, Spending range slicer

---

### Data Model Design

#### Relationships
The Power BI data model follows a **star schema** design:

**Fact Tables:**
- `transactions_detail` (Grain: One row per transaction)

**Dimension Tables:**
- `daily_sales` (Date dimension with aggregated metrics)
- `store_performance` (Store and date dimension)
- `top_products` (Product dimension)
- `customer_spending` (Customer dimension)

**Relationships:**
- `transactions_detail[transaction_date]` → `daily_sales[transaction_date]` (Many-to-One)
- `transactions_detail[store_location]` → `store_performance[store_location]` (Many-to-One)
- `transactions_detail[product_id]` → `top_products[product_id]` (Many-to-One)
- `transactions_detail[customer_id]` → `customer_spending[customer_id]` (Many-to-One)

---

### Performance Optimizations

#### 1. Data Model Optimizations
- **Aggregations:** Pre-aggregated tables (Gold layer) reduce query load
- **Column Data Types:** Optimized data types for memory efficiency
- **Remove Unused Columns:** Only essential columns imported
- **Disable Auto Date/Time:** Manual date table for better control

#### 2. DAX Optimizations
- **Variables:** Use VAR to store intermediate calculations
- **CALCULATE vs FILTER:** Use CALCULATE for better query plan
- **Avoid Iterators:** Use aggregation functions instead of row-by-row iteration
- **Measure Groups:** Organize measures into display folders

#### 3. Visual Optimizations
- **Limit Data Points:** Use Top N filtering for large datasets
- **Appropriate Visual Types:** Choose visuals that render efficiently
- **Reduce Tooltips:** Minimize custom tooltip complexity
- **Conditional Formatting:** Use rules-based instead of field-based

#### 4. Query Folding
- **Direct Query vs Import:** Use Import mode for better performance
- **Native Queries:** Leverage data source optimizations
- **Incremental Refresh:** Configure for large fact tables

---

### Refresh Strategy

#### Scheduled Refresh
- **Frequency:** Daily at 2:00 AM
- **Incremental Refresh:** Last 7 days (sliding window)
- **Full Refresh:** Weekly on Sundays

#### Data Gateway
- **Connection Mode:** Import (for optimal performance)
- **Credentials:** Service account with read-only access
- **Timeout:** 30 minutes for large datasets

---

### Key Insights & Use Cases

#### For Sales Managers
- Monitor daily sales trends and identify anomalies
- Compare store performance and allocate resources
- Track top-performing products for inventory planning

#### For Marketing Teams
- Identify high-value customer segments for targeted campaigns
- Analyze product category performance for promotional strategies
- Understand customer purchasing patterns

#### For Executive Leadership
- Track overall business performance with KPIs
- Make data-driven decisions on store expansion
- Monitor revenue growth and profitability trends

---

### Filters & Slicers

**Global Filters:**
- Date Range (Calendar slicer)
- Store Location (Multi-select dropdown)
- Product Category (Multi-select dropdown)

**Page-Level Filters:**
- Customer Segment
- Revenue Range
- Transaction Count Range

**Visual-Level Filters:**
- Top N products (configurable)
- Minimum transaction threshold

---

### Deployment Notes

1. **Data Source Configuration:**
   - Update file paths to point to Gold layer CSV exports
   - Configure data gateway if using on-premises data source

2. **Security:**
   - Row-level security (RLS) for store managers (filter by store_location)
   - Report-level permissions for executive dashboards

3. **Mobile Layout:**
   - Optimized mobile view with key KPIs
   - Touch-friendly filters and navigation

4. **Sharing:**
   - Publish to Power BI Service workspace
   - Embed in SharePoint or Teams for easy access
   - Configure email subscriptions for stakeholders

---

### Future Enhancements

1. **Real-Time Streaming:** Integrate with streaming data sources
2. **Predictive Analytics:** Add forecasting models for sales predictions
3. **What-If Analysis:** Parameter-based scenario modeling
4. **Drill-Through Pages:** Detailed transaction-level analysis
5. **Bookmarks:** Save and share specific views/filters
6. **Q&A Visual:** Natural language query interface

---

### Support & Maintenance

**Contact:** Data Engineering Team  
**Documentation:** [Internal Wiki Link]  
**Issue Tracking:** [Jira Project Link]  
**Last Updated:** November 2025
"""
    
    doc_file = f"{DOCS_PATH}/PowerBI_Dashboard_Documentation.md"
    with open(doc_file, 'w') as f:
        f.write(doc_content)
    
    print(f"✓ Power BI documentation saved to: {doc_file}\n")
    return doc_file

def create_powerbi_instructions():
    """Create step-by-step instructions for creating the Power BI dashboard"""
    print("Creating Power BI setup instructions...")
    
    instructions = """# Power BI Dashboard Setup Instructions
## Step-by-Step Guide to Creating the FinchMart Sales Dashboard

### Prerequisites
- Power BI Desktop installed (latest version)
- Access to the Gold layer CSV exports
- Basic understanding of Power BI interface

---

### Step 1: Import Data

1. **Open Power BI Desktop**
2. Click **Get Data** → **Text/CSV**
3. Import the following files in order:
   - `daily_sales.csv`
   - `store_performance.csv`
   - `top_products.csv`
   - `customer_spending.csv`
   - `transactions_detail.csv`

4. **Transform Data (Power Query Editor):**
   - For `daily_sales.csv`:
     - Change `transaction_date` to Date type
     - Change `total_sales` to Decimal Number
     - Change `avg_transaction_value` to Decimal Number
   
   - For `store_performance.csv`:
     - Change `transaction_date` to Date type
     - Change `total_sales` to Decimal Number
   
   - For `top_products.csv`:
     - Change `transaction_date` to Date type
     - Change `total_revenue` to Decimal Number
   
   - For `customer_spending.csv`:
     - Change `total_spent` to Decimal Number
     - Change `avg_transaction_value` to Decimal Number
     - Change `first_purchase_date` and `last_purchase_date` to DateTime
   
   - For `transactions_detail.csv`:
     - Change `transaction_timestamp` to DateTime
     - Change `total_amount` to Decimal Number

5. Click **Close & Apply**

---

### Step 2: Create Data Model

1. **Go to Model View** (left sidebar icon)

2. **Create Relationships:**
   - Drag `transactions_detail[transaction_timestamp]` to `daily_sales[transaction_date]`
     - Cardinality: Many to One
     - Cross filter direction: Single
   
   - Drag `transactions_detail[store_location]` to `store_performance[store_location]`
     - Cardinality: Many to One
   
   - Drag `transactions_detail[product_id]` to `top_products[product_id]`
     - Cardinality: Many to One
   
   - Drag `transactions_detail[customer_id]` to `customer_spending[customer_id]`
     - Cardinality: Many to One

3. **Hide Unnecessary Columns:**
   - Right-click on foreign key columns → **Hide in report view**

---

### Step 3: Create DAX Measures

1. **Create a Measures Table:**
   - Home → Enter Data → Create blank table named "Measures"

2. **Add Key Measures:**

```dax
Total Sales = SUM(daily_sales[total_sales])

Total Transactions = SUM(daily_sales[transaction_count])

Average Transaction Value = AVERAGE(daily_sales[avg_transaction_value])

Total Customers = DISTINCTCOUNT(customer_spending[customer_id])

Total Revenue = SUM(transactions_detail[total_amount])

Sales Growth % = 
VAR CurrentSales = [Total Sales]
VAR PreviousSales = CALCULATE([Total Sales], DATEADD(daily_sales[transaction_date], -1, DAY))
RETURN DIVIDE(CurrentSales - PreviousSales, PreviousSales, 0)

High Value Customers = 
CALCULATE(
    DISTINCTCOUNT(customer_spending[customer_id]),
    customer_spending[total_spent] > AVERAGE(customer_spending[total_spent])
)

Top Store = 
CALCULATE(
    FIRSTNONBLANK(store_performance[store_location], 1),
    TOPN(1, ALL(store_performance), [Total Sales], DESC)
)
```

---

### Step 4: Create Visualizations

#### Page 1: Sales Overview

1. **Add KPI Cards (Top Row):**
   - Insert → Card visual
   - Add these measures: Total Sales, Total Transactions, Average Transaction Value, Total Customers
   - Format: Large font, bold, add data labels

2. **Sales Trend Line Chart:**
   - Insert → Line Chart
   - X-axis: `daily_sales[transaction_date]`
   - Y-axis: `[Total Sales]`
   - Format: Add data labels, gridlines, title

3. **Store Performance Bar Chart:**
   - Insert → Clustered Bar Chart
   - Y-axis: `store_performance[store_location]`
   - X-axis: `[Total Sales]`
   - Format: Data labels, sort descending

4. **Top Products Table:**
   - Insert → Table
   - Columns: `product_name`, `product_category`, `total_revenue`, `revenue_rank`
   - Format: Conditional formatting on revenue (data bars)

5. **Customer Scatter Plot:**
   - Insert → Scatter Chart
   - X-axis: `customer_spending[transaction_count]`
   - Y-axis: `customer_spending[total_spent]`
   - Legend: `customer_spending[avg_transaction_value]` (binned)
   - Size: `customer_spending[total_items_purchased]`

---

### Step 5: Add Filters & Slicers

1. **Date Range Slicer:**
   - Insert → Slicer
   - Field: `daily_sales[transaction_date]`
   - Format: Between slicer style

2. **Store Location Slicer:**
   - Insert → Slicer
   - Field: `store_performance[store_location]`
   - Format: Dropdown style

3. **Product Category Slicer:**
   - Insert → Slicer
   - Field: `top_products[product_category]`
   - Format: List style

---

### Step 6: Format Dashboard

1. **Apply Theme:**
   - View → Themes → Choose a professional theme (e.g., Executive)

2. **Add Title:**
   - Insert → Text Box
   - Text: "FinchMart Sales Analytics Dashboard"
   - Format: Large font, bold, centered

3. **Align Visuals:**
   - Select multiple visuals → Format → Align → Distribute horizontally/vertically

4. **Add Background:**
   - Format → Canvas background → Choose subtle color

---

### Step 7: Configure Interactions

1. **Edit Interactions:**
   - Select a visual → Format → Edit interactions
   - Configure which visuals filter others (e.g., date slicer filters all)

2. **Drill-Through:**
   - Create a detail page for transaction-level analysis
   - Add drill-through field: `customer_id` or `product_id`

---

### Step 8: Optimize Performance

1. **Reduce Visual Count:** Limit to 10-15 visuals per page
2. **Use Aggregations:** Rely on Gold layer aggregations
3. **Limit Data:** Use Top N filters where appropriate
4. **Disable Auto Date/Time:** File → Options → Current File → Data Load

---

### Step 9: Test & Validate

1. **Test Filters:** Ensure slicers work correctly
2. **Validate Data:** Cross-check totals with source data
3. **Test Interactions:** Click visuals to verify cross-filtering
4. **Mobile View:** Create optimized mobile layout

---

### Step 10: Publish & Share

1. **Save File:** File → Save As → `FinchMart_Sales_Dashboard.pbix`
2. **Publish:** Home → Publish → Select workspace
3. **Configure Refresh:** Power BI Service → Dataset settings → Schedule refresh
4. **Share:** Create app or share dashboard link with stakeholders

---

### Troubleshooting

**Issue: Relationships not working**
- Solution: Check cardinality and cross-filter direction

**Issue: Slow performance**
- Solution: Reduce data volume, use aggregations, optimize DAX

**Issue: Incorrect totals**
- Solution: Check for duplicate relationships, verify measure logic

**Issue: Visuals not updating**
- Solution: Refresh data, check filter context

---

### Additional Resources

- [Power BI Documentation](https://docs.microsoft.com/power-bi/)
- [DAX Guide](https://dax.guide/)
- [Power BI Community](https://community.powerbi.com/)
"""
    
    instructions_file = f"{DOCS_PATH}/PowerBI_Setup_Instructions.md"
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"✓ Power BI setup instructions saved to: {instructions_file}\n")
    return instructions_file

def main():
    print("=" * 80)
    print("Creating Power BI Dashboard Documentation")
    print("=" * 80)
    print()
    
    # Load data
    daily_sales, store_performance, top_products, customer_spending, transactions = load_data()
    
    # Create visualizations
    mockup_file = create_visualizations(daily_sales, store_performance, top_products, customer_spending)
    
    # Create documentation
    doc_file = create_powerbi_documentation()
    instructions_file = create_powerbi_instructions()
    
    print("=" * 80)
    print("Power BI Documentation Complete")
    print("=" * 80)
    print(f"✓ Dashboard mockup: {mockup_file}")
    print(f"✓ Documentation: {doc_file}")
    print(f"✓ Setup instructions: {instructions_file}")
    print()

if __name__ == "__main__":
    main()
