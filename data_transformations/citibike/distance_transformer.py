from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import asin, col, cos, radians, sin, sqrt, lit, round

METERS_PER_FOOT = 0.3048
FEET_PER_MILE = 5280
EARTH_RADIUS_IN_METERS = 6371e3
METERS_PER_MILE = METERS_PER_FOOT * FEET_PER_MILE


def compute_distance(_spark: SparkSession, dataframe: DataFrame) -> DataFrame:
    # Convert latitude and longitude from degrees to radians
    df_with_radians = dataframe.withColumn(
        "start_lat_rad", radians(col("start_station_latitude"))
    ).withColumn(
        "start_lon_rad", radians(col("start_station_longitude"))
    ).withColumn(
        "end_lat_rad", radians(col("end_station_latitude"))
    ).withColumn(
        "end_lon_rad", radians(col("end_station_longitude"))
    )
    
    # Calculate differences
    df_with_diffs = df_with_radians.withColumn(
        "delta_lat", col("end_lat_rad") - col("start_lat_rad")
    ).withColumn(
        "delta_lon", col("end_lon_rad") - col("start_lon_rad")
    )
    
    # Apply Haversine formula
    # a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
    # c = 2 * asin(sqrt(a))
    # distance = R * c
    df_with_haversine = df_with_diffs.withColumn(
        "a",
        sin(col("delta_lat") / 2) ** 2
        + cos(col("start_lat_rad"))
        * cos(col("end_lat_rad"))
        * sin(col("delta_lon") / 2) ** 2
    ).withColumn(
        "c", 2 * asin(sqrt(col("a")))
    ).withColumn(
        "distance_meters", lit(EARTH_RADIUS_IN_METERS) * col("c")
    )
    
    # Convert meters to miles and round to 2 decimal places
    df_with_distance = df_with_haversine.withColumn(
        "distance", round(col("distance_meters") / METERS_PER_MILE, 2)
    )
    
    # Drop intermediate columns
    final_df = df_with_distance.drop(
        "start_lat_rad", "start_lon_rad", "end_lat_rad", "end_lon_rad",
        "delta_lat", "delta_lon", "a", "c", "distance_meters"
    )
    
    return final_df


def run(
    spark: SparkSession, input_dataset_path: str, transformed_dataset_path: str
) -> None:
    input_dataset = spark.read.parquet(input_dataset_path)
    input_dataset.show()

    dataset_with_distances = compute_distance(spark, input_dataset)
    dataset_with_distances.show()

    dataset_with_distances.write.parquet(transformed_dataset_path, mode="append")
