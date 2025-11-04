# Power BI Dashboard Documentation
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
