# Power BI Dashboard Setup Instructions
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
