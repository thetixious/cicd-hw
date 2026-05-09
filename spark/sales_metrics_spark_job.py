from __future__ import annotations

import sys
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


SPARK_MASTER = "spark://spark-master:7077"


def build_orders(run_date: str) -> list[tuple[str, str, int, float, float, str]]:
    day = int(run_date[-2:])
    products = [
        ("laptop", 1250.0),
        ("monitor", 430.0),
        ("keyboard", 110.0),
        ("mouse", 55.0),
        ("webcam", 95.0),
    ]

    orders = []
    for index, (product, price) in enumerate(products, start=1):
        quantity = (day + index) % 5 + 1
        discount = 0.15 if product == "laptop" and day % 2 == 0 else 0.05
        status = "paid" if quantity >= 2 else "cancelled"
        orders.append((f"{run_date.replace('-', '')}-{index}", product, quantity, price, discount, status))

    return orders


def main(run_date: str) -> None:
    spark = (
        SparkSession.builder.appName("sales_metrics_spark_job")
        .master(SPARK_MASTER)
        .getOrCreate()
    )

    try:
        orders = spark.createDataFrame(
            build_orders(run_date),
            ["order_id", "product", "quantity", "unit_price", "discount", "status"],
        )

        paid_orders = orders.where(F.col("status") == "paid").withColumn(
            "revenue",
            F.round(F.col("quantity") * F.col("unit_price") * (1 - F.col("discount")), 2),
        )

        product_revenue = paid_orders.groupBy("product").agg(
            F.round(F.sum("revenue"), 2).alias("revenue"),
            F.sum("quantity").alias("items_sold"),
        )

        totals = paid_orders.agg(
            F.count("*").alias("paid_orders"),
            F.round(F.sum("revenue"), 2).alias("total_revenue"),
            F.round(F.avg("revenue"), 2).alias("average_order_value"),
        ).first()

        total_orders = orders.count()
        best_product = product_revenue.orderBy(F.desc("revenue")).first()
        revenue_rows = product_revenue.orderBy("product").collect()

        report_path = Path("/opt/airflow/reports") / f"spark_sales_metrics_{run_date.replace('-', '')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            "\n".join(
                [
                    f"# Spark sales report for {run_date}",
                    "",
                    f"Total orders: {total_orders}",
                    f"Paid orders: {totals.paid_orders}",
                    f"Conversion rate: {totals.paid_orders / total_orders:.2f}",
                    f"Total revenue: {totals.total_revenue:.2f}",
                    f"Average order value: {totals.average_order_value:.2f}",
                    f"Best product: {best_product.product}",
                    "",
                    "Revenue by product:",
                    *[
                        f"- {row.product}: revenue={row.revenue:.2f}, items_sold={row.items_sold}"
                        for row in revenue_rows
                    ],
                    "",
                ]
            ),
            encoding="utf-8",
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-05-09")
