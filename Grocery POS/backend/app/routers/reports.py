from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.auth import require_owner, get_optional_user
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.sale import Sale, SaleItem, SaleStatus, SaleReturn
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.product import Product
from app.models.category import Category
from app.models.purchase_order import PurchaseOrder

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

# --- 1. Executive Summary (Restricted to Owner for RBAC) ---

@router.get("/summary")
def get_executive_summary(
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Provide high-level financial, inventory, and sales analytics for the Store Owner."""
    total_sales_count = db.query(Order).count()
    revenue_sum = db.query(func.sum(Order.total_amount)).scalar() or 0.0
    tax_sum = db.query(func.sum(Order.tax_amount)).scalar() or 0.0
    discount_sum = db.query(func.sum(Order.discount_amount)).scalar() or 0.0

    products = db.query(Product).filter(Product.is_active == True).all()
    total_catalog_items = len(products)
    inventory_retail_value = sum(p.price * p.stock_quantity for p in products)
    inventory_cost_value = sum((p.cost_price or 0.0) * p.stock_quantity for p in products)
    estimated_unrealized_profit = inventory_retail_value - inventory_cost_value

    low_stock_count = sum(1 for p in products if p.stock_quantity <= p.min_stock_alert)
    today = datetime.utcnow().date()
    expiring_soon_threshold = today + timedelta(days=30)
    expiring_soon_count = sum(1 for p in products if p.expiry_date and p.expiry_date <= expiring_soon_threshold)

    category_counts = (
        db.query(Category.name, func.count(Product.id))
        .join(Product, Product.category_id == Category.id)
        .group_by(Category.name)
        .all()
    )

    return {
        "store_kpis": {
            "total_revenue": round(revenue_sum, 2),
            "total_transactions": total_sales_count,
            "total_tax_collected": round(tax_sum, 2),
            "total_discounts_given": round(discount_sum, 2),
            "net_revenue": round(revenue_sum - tax_sum, 2),
        },
        "inventory_kpis": {
            "total_catalog_items": total_catalog_items,
            "inventory_retail_valuation": round(inventory_retail_value, 2),
            "inventory_cost_valuation": round(inventory_cost_value, 2),
            "projected_profit": round(estimated_unrealized_profit, 2),
            "profit_margin_pct": round((estimated_unrealized_profit / inventory_retail_value * 100), 1) if inventory_retail_value > 0 else 0,
            "low_stock_alerts": low_stock_count,
            "expiring_soon_items": expiring_soon_count,
        },
        "categories_distribution": [
            {"category": name, "item_count": count} for name, count in category_counts
        ],
        "generated_at": datetime.utcnow().isoformat(),
        "generated_by": current_user.full_name,
    }

# --- 2. Live Dashboard Analytics Endpoint ---

@router.get("/dashboard")
def get_dashboard_metrics(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Provide real-time metrics for Dashboard: Today's sales, Cash vs Card vs UPI, Low stock, and P&L estimations."""
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)

    # A. Today's sales
    today_sales = db.query(Sale).filter(Sale.created_at >= today_start).all()
    today_revenue = sum(s.grand_total for s in today_sales)
    today_orders_count = len(today_sales)
    today_items_count = sum(sum(item.quantity for item in s.items) for s in today_sales)
    avg_basket = round(today_revenue / today_orders_count, 2) if today_orders_count > 0 else 0.0

    # B. Total Cash vs Card vs UPI vs Split
    payments = db.query(Payment).all()
    cash_total = sum(p.amount for p in payments if p.payment_method == PaymentMethod.CASH and p.status != PaymentStatus.REFUNDED)
    cash_count = sum(1 for p in payments if p.payment_method == PaymentMethod.CASH and p.status != PaymentStatus.REFUNDED)

    card_total = sum(p.amount for p in payments if p.payment_method == PaymentMethod.CARD and p.status != PaymentStatus.REFUNDED)
    card_count = sum(1 for p in payments if p.payment_method == PaymentMethod.CARD and p.status != PaymentStatus.REFUNDED)

    upi_total = sum(p.amount for p in payments if p.payment_method == PaymentMethod.UPI and p.status != PaymentStatus.REFUNDED)
    upi_count = sum(1 for p in payments if p.payment_method == PaymentMethod.UPI and p.status != PaymentStatus.REFUNDED)

    split_sales = [s for s in db.query(Sale).all() if len(s.payments) > 1 or s.status == "SPLIT"]
    split_total = sum(s.grand_total for s in split_sales)
    split_count = len(split_sales)

    # C. Low-Stock Products (items with stock <= 50.0 or <= min_stock_alert)
    low_stock_query = db.query(Product).filter(
        Product.is_active == True,
        Product.stock_quantity <= 50.0
    ).order_by(Product.stock_quantity.asc())

    low_stock_count = low_stock_query.count()
    low_stock_items = [
        {
            "id": p.id,
            "name": p.name,
            "barcode": p.barcode,
            "stock_quantity": p.stock_quantity,
            "unit": p.unit,
            "min_stock_alert": p.min_stock_alert,
            "category": p.category.name if p.category else "General",
            "price": p.price,
        }
        for p in low_stock_query.limit(10).all()
    ]

    # D. Profit & Loss Estimations
    sale_items = db.query(SaleItem).all()
    gross_sales_revenue = sum(si.line_total for si in sale_items)
    cost_of_goods_sold = sum((si.cost_price or 0.0) * si.quantity for si in sale_items)
    gross_profit = gross_sales_revenue - cost_of_goods_sold
    margin_pct = round((gross_profit / gross_sales_revenue * 100), 1) if gross_sales_revenue > 0 else 0.0

    returns = db.query(SaleReturn).all()
    total_refunded = sum(r.refund_amount for r in returns)
    net_profit = max(0.0, gross_profit - total_refunded)

    # E. 7-Day Sales Trend (Weekly)
    days_data = []
    for i in range(6, -1, -1):
        target_day = (now - timedelta(days=i)).date()
        day_start = datetime(target_day.year, target_day.month, target_day.day)
        day_end = day_start + timedelta(days=1)

        day_sales = db.query(Sale).filter(Sale.created_at >= day_start, Sale.created_at < day_end).all()
        day_rev = sum(s.grand_total for s in day_sales)
        day_cogs = sum(sum((it.cost_price or 0.0) * it.quantity for it in s.items) for s in day_sales)
        day_profit = max(0.0, day_rev - day_cogs)

        days_data.append({
            "date": target_day.strftime("%d %b"),
            "day": target_day.strftime("%a"),
            "revenue": round(day_rev, 2),
            "orders": len(day_sales),
            "profit": round(day_profit, 2),
        })

    # F. Category Distribution
    category_data = (
        db.query(Category.name, func.count(Product.id), func.sum(Product.price * Product.stock_quantity))
        .join(Product, Product.category_id == Category.id)
        .group_by(Category.name)
        .all()
    )
    categories_chart = [
        {
            "name": cat_name,
            "product_count": p_count,
            "valuation": round(val or 0.0, 2),
        }
        for cat_name, p_count, val in category_data
    ]

    return {
        "today_sales": {
            "total_revenue": round(today_revenue, 2),
            "transactions_count": today_orders_count,
            "items_sold_count": round(today_items_count, 2),
            "avg_basket_value": avg_basket,
        },
        "payment_methods": {
            "cash": {"total": round(cash_total, 2), "count": cash_count},
            "card": {"total": round(card_total, 2), "count": card_count},
            "upi": {"total": round(upi_total, 2), "count": upi_count},
            "split": {"total": round(split_total, 2), "count": split_count},
        },
        "low_stock": {
            "total_count": low_stock_count,
            "products": low_stock_items,
        },
        "profit_loss": {
            "gross_revenue": round(gross_sales_revenue, 2),
            "cost_of_goods_sold": round(cost_of_goods_sold, 2),
            "gross_profit": round(gross_profit, 2),
            "margin_pct": margin_pct,
            "total_refunded": round(total_refunded, 2),
            "net_profit": round(net_profit, 2),
        },
        "weekly_trend": days_data,
        "categories_chart": categories_chart,
        "server_time": now.isoformat(),
    }

# --- 3. Top Products / Best Sellers ---

@router.get("/top-products")
@router.get("/best-sellers")
def get_top_selling_products(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Retrieve top selling products by transaction velocity and total sales revenue."""
    top_items = (
        db.query(
            SaleItem.product_name,
            func.sum(SaleItem.quantity).label("units_sold"),
            func.sum(SaleItem.line_total).label("total_sales_value"),
            func.avg(SaleItem.unit_price).label("avg_unit_price")
        )
        .group_by(SaleItem.product_name)
        .order_by(desc("units_sold"))
        .limit(limit)
        .all()
    )

    if not top_items:
        # Fallback to OrderItem if SaleItem has no rows yet
        top_items = (
            db.query(
                OrderItem.product_name,
                func.sum(OrderItem.quantity).label("units_sold"),
                func.sum(OrderItem.total).label("total_sales_value"),
                func.avg(OrderItem.unit_price).label("avg_unit_price")
            )
            .group_by(OrderItem.product_name)
            .order_by(desc("units_sold"))
            .limit(limit)
            .all()
        )

    return [
        {
            "product_name": item[0],
            "units_sold": float(item[1] or 0),
            "total_sales_value": round(float(item[2] or 0), 2),
            "avg_unit_price": round(float(item[3] or 0), 2),
        }
        for item in top_items
    ]

# --- 4. Sales Trends (Daily & Monthly) ---

@router.get("/sales-trends")
def get_sales_trends(
    period: str = Query("daily", pattern="^(daily|monthly)$"),
    db: Session = Depends(get_db)
):
    """Provide historical sales trends over daily or monthly buckets."""
    sales = db.query(Sale).order_by(Sale.created_at.asc()).all()

    if period == "monthly":
        monthly_map = {}
        for s in sales:
            month_key = s.created_at.strftime("%b %Y")
            if month_key not in monthly_map:
                monthly_map[month_key] = {"month": month_key, "revenue": 0.0, "orders": 0, "tax": 0.0, "profit": 0.0}
            monthly_map[month_key]["revenue"] += s.grand_total
            monthly_map[month_key]["orders"] += 1
            monthly_map[month_key]["tax"] += s.tax_amount
            cogs = sum((it.cost_price or 0.0) * it.quantity for it in s.items)
            monthly_map[month_key]["profit"] += max(0.0, s.grand_total - cogs)

        return [
            {
                "label": v["month"],
                "revenue": round(v["revenue"], 2),
                "orders": v["orders"],
                "tax": round(v["tax"], 2),
                "profit": round(v["profit"], 2),
            }
            for v in monthly_map.values()
        ]
    else:
        # Daily trend (last 14 days)
        now = datetime.utcnow()
        daily_list = []
        for i in range(13, -1, -1):
            day = (now - timedelta(days=i)).date()
            d_start = datetime(day.year, day.month, day.day)
            d_end = d_start + timedelta(days=1)

            d_sales = [s for s in sales if d_start <= s.created_at < d_end]
            d_rev = sum(s.grand_total for s in d_sales)
            d_tax = sum(s.tax_amount for s in d_sales)
            d_cogs = sum(sum((it.cost_price or 0.0) * it.quantity for it in s.items) for s in d_sales)
            d_profit = max(0.0, d_rev - d_cogs)

            daily_list.append({
                "label": day.strftime("%d %b"),
                "date": day.isoformat(),
                "revenue": round(d_rev, 2),
                "orders": len(d_sales),
                "tax": round(d_tax, 2),
                "profit": round(d_profit, 2),
            })
        return daily_list

# --- 5. Audit Logs Trail ---

@router.get("/audit-logs")
def get_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve unified chronologically-sorted audit logs of all store operational events."""
    logs = []

    # 1. Sales Logs
    sales = db.query(Sale).order_by(Sale.created_at.desc()).limit(limit).all()
    for s in sales:
        cashier = s.cashier.full_name if s.cashier else "Cashier"
        logs.append({
            "id": f"SALE-{s.id}",
            "event_type": "CHECKOUT",
            "action": f"Sale Completed ({s.invoice_number})",
            "details": f"Generated bill for ₹{s.grand_total} ({len(s.items)} items) via {s.status.value}",
            "user_name": cashier,
            "timestamp": s.created_at,
            "status": "SUCCESS",
            "severity": "INFO",
        })

    # 2. Returns Logs
    returns = db.query(SaleReturn).order_by(SaleReturn.created_at.desc()).limit(limit).all()
    for r in returns:
        logs.append({
            "id": f"RET-{r.id}",
            "event_type": "RETURN",
            "action": f"Customer Return Processed ({r.return_number})",
            "details": f"Refund of ₹{r.refund_amount} issued via {r.refund_method}. Stock restored to catalog.",
            "user_name": "Store Terminal",
            "timestamp": r.created_at,
            "status": "REFUNDED",
            "severity": "WARNING",
        })

    # 3. Procurement PO Logs
    pos = db.query(PurchaseOrder).order_by(PurchaseOrder.order_date.desc()).limit(limit).all()
    for po in pos:
        logs.append({
            "id": f"PO-{po.id}",
            "event_type": "PROCUREMENT",
            "action": f"Purchase Order {po.po_number} ({po.status.value})",
            "details": f"Supplier: {po.supplier.name if po.supplier else 'N/A'} - Total: ₹{po.total_amount}",
            "user_name": "Manager",
            "timestamp": po.order_date,
            "status": po.status.value,
            "severity": "SUCCESS" if po.status.value == "RECEIVED" else "INFO",
        })

    # Sort all events chronologically descending
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    return logs[:limit]
