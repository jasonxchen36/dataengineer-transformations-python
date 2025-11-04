"""
FinchMart Sales ETL Pipeline Runner (Simplified for Local Execution)
Executes the complete medallion architecture pipeline: Bronze -> Silver -> Gold
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_timestamp, when, coalesce, lit, row_number, current_timestamp,
    sum as _sum, avg, count, max as _max, min as _min, date_format, to_date,
    round as spark_round, input_file_name
)
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType
import os
import time

# Configuration
BASE_PATH = "/home/ubuntu/dataengineer-transformations-python/finchmart_sales_etl"
RAW_DATA_PATH = f"{BASE_PATH}/data/raw"
BRONZE_PATH = f"{BASE_PATH}/data/bronze/sales_transactions"
SILVER_PATH = f"{BASE_PATH}/data/silver/sales_transactions_clean"
GOLD_DAILY_PATH = f"{BASE_PATH}/data/gold/daily_sales"
GOLD_STORE_PATH = f"{BASE_PATH}/data/gold/store_performance"
GOLD_PRODUCTS_PATH = f"{BASE_PATH}/data/gold/top_products"
GOLD_CUSTOMERS_PATH = f"{BASE_PATH}/data/gold/customer_spending"
PRODUCT_REF_PATH = f"{BASE_PATH}/data/raw/Product_Table.csv"
EXPORT_PATH = f"{BASE_PATH}/data/gold/powerbi_export"

def initialize_spark():
    """Initialize Spark session"""
    print("=" * 80)
    print("Initializing Spark Session")
    print("=" * 80)
    
    spark = SparkSession.builder \
        .appName("FinchMart-ETL-Pipeline") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
    
    print(f"✓ Spark Version: {spark.version}")
    print(f"✓ Spark configured successfully\n")
    
    return spark

def bronze_layer_ingestion(spark):
    """Bronze Layer: Ingest raw CSV files"""
    print("=" * 80)
    print("BRONZE LAYER: Raw Data Ingestion")
    print("=" * 80)
    
    # Define schema
    sales_schema = StructType([
        StructField("transaction_id", StringType(), False),
        StructField("timestamp", StringType(), False),
        StructField("customer_id", StringType(), False),
        StructField("product_id", StringType(), False),
        StructField("product_category", StringType(), True),
        StructField("price", FloatType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("payment_method", StringType(), True),
        StructField("store_location", StringType(), True)
    ])
    
    # Read CSV files
    print(f"Reading CSV files from: {RAW_DATA_PATH}")
    raw_sales_df = spark.read \
        .format("csv") \
        .option("header", "true") \
        .schema(sales_schema) \
        .load(f"{RAW_DATA_PATH}/Mock_Sales_Data*.csv")
    
    # Add metadata columns
    bronze_sales_df = raw_sales_df \
        .withColumn("ingestion_timestamp", current_timestamp()) \
        .withColumn("source_file", input_file_name())
    
    print(f"✓ Loaded {bronze_sales_df.count()} records from CSV files")
    
    # Write to Bronze layer
    print(f"Writing to Bronze layer: {BRONZE_PATH}")
    bronze_sales_df.write \
        .format("parquet") \
        .mode("overwrite") \
        .save(BRONZE_PATH)
    
    # Verify
    bronze_df = spark.read.format("parquet").load(BRONZE_PATH)
    print(f"✓ Bronze layer created with {bronze_df.count()} records")
    print(f"✓ Distinct transaction IDs: {bronze_df.select('transaction_id').distinct().count()}")
    print(f"✓ Source files processed: {bronze_df.select('source_file').distinct().count()}\n")
    
    return bronze_df

def silver_layer_transformation(spark):
    """Silver Layer: Cleanse and enrich data"""
    print("=" * 80)
    print("SILVER LAYER: Data Cleansing and Enrichment")
    print("=" * 80)
    
    # Read Bronze layer
    print(f"Reading from Bronze layer: {BRONZE_PATH}")
    bronze_df = spark.read.format("parquet").load(BRONZE_PATH)
    print(f"✓ Loaded {bronze_df.count()} records from Bronze layer")
    
    # Read Product reference data
    print(f"Reading product reference data: {PRODUCT_REF_PATH}")
    product_df = spark.read \
        .format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(PRODUCT_REF_PATH)
    
    product_df = product_df \
        .withColumnRenamed("product_id", "prod_id") \
        .withColumnRenamed("product_category", "ref_category") \
        .withColumnRenamed("base_price", "list_price")
    
    print(f"✓ Loaded {product_df.count()} products from reference table")
    
    # Step 1: Handle timestamp conversion
    print("\nCleansing Step 1: Timestamp validation")
    cleansed_df = bronze_df \
        .withColumn("transaction_timestamp", to_timestamp(col("timestamp"), "yyyy-MM-dd'T'HH:mm:ss.SSSSSS")) \
        .filter(col("transaction_timestamp").isNotNull())
    print(f"✓ Records after timestamp validation: {cleansed_df.count()}")
    
    # Step 2: Remove duplicates
    print("\nCleansing Step 2: Deduplication")
    window_spec = Window.partitionBy("transaction_id").orderBy(col("ingestion_timestamp").desc())
    deduplicated_df = cleansed_df \
        .withColumn("row_num", row_number().over(window_spec)) \
        .filter(col("row_num") == 1) \
        .drop("row_num")
    print(f"✓ Records after deduplication: {deduplicated_df.count()}")
    
    # Step 3: Handle null values and data quality
    print("\nCleansing Step 3: Data quality checks")
    quality_df = deduplicated_df \
        .withColumn("payment_method", coalesce(col("payment_method"), lit("Unknown"))) \
        .withColumn("store_location", coalesce(col("store_location"), lit("Unknown"))) \
        .withColumn("quantity", when(col("quantity") > 0, col("quantity")).otherwise(1)) \
        .withColumn("price", when(col("price") > 0, col("price")).otherwise(0.0)) \
        .filter(col("transaction_id").isNotNull()) \
        .filter(col("customer_id").isNotNull()) \
        .filter(col("product_id").isNotNull())
    print(f"✓ Records after quality checks: {quality_df.count()}")
    
    # Step 4: Enrich with product data
    print("\nEnrichment: Joining with product reference data")
    enriched_df = quality_df \
        .join(product_df, quality_df.product_id == product_df.prod_id, "left") \
        .select(
            col("transaction_id"),
            col("transaction_timestamp"),
            col("customer_id"),
            col("product_id"),
            col("product_name"),
            coalesce(col("ref_category"), col("product_category")).alias("product_category"),
            col("price").alias("transaction_price"),
            col("list_price"),
            col("quantity"),
            (col("price") * col("quantity")).alias("total_amount"),
            col("payment_method"),
            col("store_location"),
            col("source_file"),
            col("ingestion_timestamp")
        ) \
        .withColumn("total_amount", spark_round(col("total_amount"), 2)) \
        .withColumn("processed_timestamp", current_timestamp())
    
    print(f"✓ Records after enrichment: {enriched_df.count()}")
    
    # Write to Silver layer
    print(f"\nWriting to Silver layer: {SILVER_PATH}")
    enriched_df.write \
        .format("parquet") \
        .mode("overwrite") \
        .save(SILVER_PATH)
    
    # Verify and report
    silver_df = spark.read.format("parquet").load(SILVER_PATH)
    print(f"✓ Silver layer created with {silver_df.count()} records")
    
    stats = silver_df.agg(
        _sum("total_amount").alias("total_revenue"),
        avg("total_amount").alias("avg_transaction")
    ).first()
    
    unique_customers = silver_df.select("customer_id").distinct().count()
    
    print(f"✓ Total Revenue: ${stats['total_revenue']:,.2f}")
    print(f"✓ Average Transaction: ${stats['avg_transaction']:,.2f}")
    print(f"✓ Unique Customers: {unique_customers}\n")
    
    return silver_df

def gold_layer_aggregation(spark):
    """Gold Layer: Create business aggregations"""
    print("=" * 80)
    print("GOLD LAYER: Business Aggregations")
    print("=" * 80)
    
    # Read Silver layer
    print(f"Reading from Silver layer: {SILVER_PATH}")
    silver_df = spark.read.format("parquet").load(SILVER_PATH)
    print(f"✓ Loaded {silver_df.count()} records from Silver layer")
    
    # 1. Daily Sales Aggregation
    print("\n1. Creating Daily Sales Aggregation...")
    daily_sales_df = silver_df \
        .withColumn("transaction_date", to_date(col("transaction_timestamp"))) \
        .groupBy("transaction_date") \
        .agg(
            _sum("total_amount").alias("total_sales"),
            count("transaction_id").alias("transaction_count"),
            _sum("quantity").alias("total_items_sold"),
            avg("total_amount").alias("avg_transaction_value")
        ) \
        .withColumn("total_sales", spark_round(col("total_sales"), 2)) \
        .withColumn("avg_transaction_value", spark_round(col("avg_transaction_value"), 2)) \
        .withColumn("updated_at", current_timestamp()) \
        .orderBy("transaction_date")
    
    daily_sales_df.write \
        .format("parquet") \
        .mode("overwrite") \
        .partitionBy("transaction_date") \
        .save(GOLD_DAILY_PATH)
    print(f"✓ Daily sales aggregation created: {daily_sales_df.count()} days")
    
    # 2. Store Performance Aggregation
    print("\n2. Creating Store Performance Aggregation...")
    store_performance_df = silver_df \
        .withColumn("transaction_date", to_date(col("transaction_timestamp"))) \
        .groupBy("transaction_date", "store_location") \
        .agg(
            _sum("total_amount").alias("total_sales"),
            count("transaction_id").alias("transaction_count"),
            _sum("quantity").alias("total_items_sold"),
            avg("total_amount").alias("avg_transaction_value")
        ) \
        .withColumn("total_sales", spark_round(col("total_sales"), 2)) \
        .withColumn("avg_transaction_value", spark_round(col("avg_transaction_value"), 2)) \
        .withColumn("updated_at", current_timestamp()) \
        .orderBy("transaction_date", col("total_sales").desc())
    
    store_performance_df.write \
        .format("parquet") \
        .mode("overwrite") \
        .partitionBy("transaction_date") \
        .save(GOLD_STORE_PATH)
    print(f"✓ Store performance aggregation created: {store_performance_df.count()} records")
    
    # 3. Top Products by Revenue
    print("\n3. Creating Top Products Aggregation...")
    products_df = silver_df \
        .withColumn("transaction_date", to_date(col("transaction_timestamp"))) \
        .groupBy("transaction_date", "product_id", "product_name", "product_category") \
        .agg(
            _sum("total_amount").alias("total_revenue"),
            _sum("quantity").alias("total_quantity_sold"),
            count("transaction_id").alias("transaction_count"),
            avg("transaction_price").alias("avg_price")
        ) \
        .withColumn("total_revenue", spark_round(col("total_revenue"), 2)) \
        .withColumn("avg_price", spark_round(col("avg_price"), 2))
    
    window_spec = Window.partitionBy("transaction_date").orderBy(col("total_revenue").desc())
    top_products_df = products_df \
        .withColumn("revenue_rank", row_number().over(window_spec)) \
        .filter(col("revenue_rank") <= 5) \
        .withColumn("updated_at", current_timestamp()) \
        .orderBy("transaction_date", "revenue_rank")
    
    top_products_df.write \
        .format("parquet") \
        .mode("overwrite") \
        .partitionBy("transaction_date") \
        .save(GOLD_PRODUCTS_PATH)
    print(f"✓ Top products aggregation created: {top_products_df.count()} records")
    
    # 4. Customer Spending Behavior
    print("\n4. Creating Customer Spending Aggregation...")
    customer_spending_df = silver_df \
        .groupBy("customer_id") \
        .agg(
            _sum("total_amount").alias("total_spent"),
            count("transaction_id").alias("transaction_count"),
            avg("total_amount").alias("avg_transaction_value"),
            _sum("quantity").alias("total_items_purchased"),
            _min("transaction_timestamp").alias("first_purchase_date"),
            _max("transaction_timestamp").alias("last_purchase_date")
        ) \
        .withColumn("total_spent", spark_round(col("total_spent"), 2)) \
        .withColumn("avg_transaction_value", spark_round(col("avg_transaction_value"), 2)) \
        .withColumn("updated_at", current_timestamp()) \
        .orderBy(col("total_spent").desc())
    
    customer_spending_df.write \
        .format("parquet") \
        .mode("overwrite") \
        .save(GOLD_CUSTOMERS_PATH)
    print(f"✓ Customer spending aggregation created: {customer_spending_df.count()} customers")
    
    # Export for Power BI
    print(f"\n5. Exporting data for Power BI to: {EXPORT_PATH}")
    
    daily_sales_df.coalesce(1).write \
        .format("csv") \
        .option("header", "true") \
        .mode("overwrite") \
        .save(f"{EXPORT_PATH}/daily_sales")
    print("✓ Daily sales exported")
    
    store_performance_df.coalesce(1).write \
        .format("csv") \
        .option("header", "true") \
        .mode("overwrite") \
        .save(f"{EXPORT_PATH}/store_performance")
    print("✓ Store performance exported")
    
    top_products_df.coalesce(1).write \
        .format("csv") \
        .option("header", "true") \
        .mode("overwrite") \
        .save(f"{EXPORT_PATH}/top_products")
    print("✓ Top products exported")
    
    customer_spending_df.coalesce(1).write \
        .format("csv") \
        .option("header", "true") \
        .mode("overwrite") \
        .save(f"{EXPORT_PATH}/customer_spending")
    print("✓ Customer spending exported")
    
    silver_df.coalesce(1).write \
        .format("csv") \
        .option("header", "true") \
        .mode("overwrite") \
        .save(f"{EXPORT_PATH}/transactions_detail")
    print("✓ Transaction details exported\n")
    
    return {
        'daily_sales': daily_sales_df,
        'store_performance': store_performance_df,
        'top_products': top_products_df,
        'customer_spending': customer_spending_df
    }

def main():
    """Execute the complete ETL pipeline"""
    start_time = time.time()
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "FinchMart Sales ETL Pipeline" + " " * 30 + "║")
    print("║" + " " * 22 + "Medallion Architecture" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    try:
        # Initialize Spark
        spark = initialize_spark()
        
        # Execute Bronze layer
        bronze_df = bronze_layer_ingestion(spark)
        
        # Execute Silver layer
        silver_df = silver_layer_transformation(spark)
        
        # Execute Gold layer
        gold_tables = gold_layer_aggregation(spark)
        
        # Final summary
        elapsed_time = time.time() - start_time
        print("=" * 80)
        print("PIPELINE EXECUTION COMPLETE")
        print("=" * 80)
        print(f"✓ Total execution time: {elapsed_time:.2f} seconds")
        print(f"✓ Bronze layer: {BRONZE_PATH}")
        print(f"✓ Silver layer: {SILVER_PATH}")
        print(f"✓ Gold layer: {BASE_PATH}/data/gold/")
        print(f"✓ Power BI exports: {EXPORT_PATH}")
        print("\nAll data is ready for Power BI dashboard creation!")
        print("=" * 80)
        
        spark.stop()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
