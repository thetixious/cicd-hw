from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context


PRODUCT_TARGETS = {
    "laptop": 2,
    "monitor": 3,
    "keyboard": 4,
    "mouse": 5,
}


@dag(
    dag_id="daily_sales_metrics",
    description="Calculates sales metrics and writes a daily markdown report.",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["homework", "sales", "metrics"],
)
def daily_sales_metrics():
    @task
    def extract_orders() -> list[dict[str, object]]:
        context = get_current_context()
        day = context["logical_date"].day

        products = {
            "laptop": 1250,
            "monitor": 430,
            "keyboard": 110,
            "mouse": 55,
        }

        orders = []
        for index, (product, price) in enumerate(products.items(), start=1):
            quantity = (day + index) % 5 + 1
            discount = 0.15 if product == "laptop" and day % 2 == 0 else 0.05
            orders.append(
                {
                    "order_id": f"{context['ds_nodash']}-{index}",
                    "product": product,
                    "quantity": quantity,
                    "unit_price": price,
                    "discount": discount,
                    "status": "paid" if quantity >= 2 else "cancelled",
                }
            )

        return orders

    @task
    def calculate_metrics(orders: list[dict[str, object]]) -> dict[str, object]:
        paid_orders = [order for order in orders if order["status"] == "paid"]
        revenue_by_product: dict[str, float] = {}

        for order in paid_orders:
            product = str(order["product"])
            revenue = (
                int(order["quantity"])
                * float(order["unit_price"])
                * (1 - float(order["discount"]))
            )
            revenue_by_product[product] = revenue_by_product.get(product, 0) + revenue

        total_revenue = round(sum(revenue_by_product.values()), 2)
        best_product = max(revenue_by_product, key=revenue_by_product.get)

        return {
            "orders_total": len(orders),
            "orders_paid": len(paid_orders),
            "conversion_rate": round(len(paid_orders) / len(orders), 2),
            "total_revenue": total_revenue,
            "average_order_value": round(total_revenue / len(paid_orders), 2),
            "average_quantity": round(mean(int(order["quantity"]) for order in paid_orders), 2),
            "best_product": best_product,
            "revenue_by_product": revenue_by_product,
        }

    @task
    def check_targets(metrics: dict[str, object]) -> dict[str, object]:
        revenue_by_product = metrics["revenue_by_product"]
        failed_products = []

        for product, target_quantity in PRODUCT_TARGETS.items():
            expected_min_revenue = target_quantity * 50
            actual_revenue = float(revenue_by_product.get(product, 0))
            if actual_revenue < expected_min_revenue:
                failed_products.append(product)

        return {
            "status": "ok" if not failed_products else "attention_required",
            "failed_products": failed_products,
        }

    @task
    def write_report(metrics: dict[str, object], target_status: dict[str, object]) -> str:
        context = get_current_context()
        report_dir = Path("/opt/airflow/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"sales_metrics_{context['ds_nodash']}.md"

        revenue_lines = [
            f"- {product}: {revenue:.2f}"
            for product, revenue in sorted(metrics["revenue_by_product"].items())
        ]

        report_path.write_text(
            "\n".join(
                [
                    f"# Sales report for {context['ds']}",
                    "",
                    f"Total orders: {metrics['orders_total']}",
                    f"Paid orders: {metrics['orders_paid']}",
                    f"Conversion rate: {metrics['conversion_rate']}",
                    f"Total revenue: {metrics['total_revenue']:.2f}",
                    f"Average order value: {metrics['average_order_value']:.2f}",
                    f"Average quantity: {metrics['average_quantity']}",
                    f"Best product: {metrics['best_product']}",
                    f"Target status: {target_status['status']}",
                    "",
                    "Revenue by product:",
                    *revenue_lines,
                    "",
                ]
            ),
            encoding="utf-8",
        )

        return str(report_path)

    orders = extract_orders()
    metrics = calculate_metrics(orders)
    target_status = check_targets(metrics)
    write_report(metrics, target_status)


daily_sales_metrics()
