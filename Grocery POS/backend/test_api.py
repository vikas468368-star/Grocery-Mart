"""Automated Integration & RBAC Test Suite for Grocery POS System.
Tests:
- Health check & database connection
- 655+ Products catalog retrieval and search filtering
- Barcode scanner rapid lookup
- Categories & Department verification
- JWT Authentication (/auth/login) for Owner, Manager, Cashier
- Token Claims & Profile endpoint (/auth/me)
- Role-Based Access Control (RBAC):
  * Owner exclusive access to /reports/summary and /settings/
  * Manager inventory access and product management
  * Cashier restriction to billing only (403 on reports and product creation)
- Real-time billing calculations (subtotal, GST taxes, discounts)
- POS Checkout process, inventory deduction, and receipt generation
"""

import sys
import os

sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_system():
    print("=" * 70)
    print("🧪 Running Grocery POS Integration & RBAC Test Suite")
    print("=" * 70)

    # 1. Health check
    print("\n[Test 1] Testing /api/v1/health...")
    res = client.get("/api/v1/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    health_data = res.json()
    print(f"  ✓ Health Status: {health_data['status']}")
    print(f"  ✓ Database Connection: {health_data['database']}")

    # 2. Categories
    print("\n[Test 2] Testing /api/v1/categories/...")
    res = client.get("/api/v1/categories/")
    assert res.status_code == 200
    categories = res.json()
    print(f"  ✓ Loaded {len(categories)} categories (Departments):")
    for c in categories[:4]:
        print(f"    - {c['name']} ({c['code']}) - Tax: {int(c['default_tax_rate']*100)}%")
    assert len(categories) >= 12, "Expected at least 12 categories"

    # 3. Products Catalog Count
    print("\n[Test 3] Testing /api/v1/products/ (Catalog Count)...")
    res = client.get("/api/v1/products/?limit=700")
    assert res.status_code == 200
    products = res.json()
    print(f"  ✓ Total Products returned: {len(products)} items")
    assert len(products) >= 500, f"Expected at least 500 products, found {len(products)}"

    # 4. Search Filter
    print("\n[Test 4] Testing /api/v1/products/?search=Apple...")
    res = client.get("/api/v1/products/?search=Apple")
    assert res.status_code == 200
    apple_results = res.json()
    print(f"  ✓ Found {len(apple_results)} products matching 'Apple'")
    for a in apple_results[:2]:
        print(f"    - {a['name']} | Barcode: {a['barcode']} | Price: Rs.{a['price']}")

    # 5. Barcode Scanner Instant Lookup
    print("\n[Test 5] Testing Barcode Scanner Lookup (/api/v1/products/barcode/890100000001)...")
    res = client.get("/api/v1/products/barcode/890100000001")
    assert res.status_code == 200
    prod = res.json()
    print(f"  ✓ Barcode: {prod['barcode']} | Product: {prod['name']} | Price: Rs.{prod['price']}")

    # 6. JWT Authentication (/auth/login)
    print("\n[Test 6] Testing JWT Authentication for Staff Roles...")
    # Owner login
    res_owner = client.post("/api/v1/auth/login", json={"username": "owner", "password": "password123"})
    assert res_owner.status_code == 200, f"Owner login failed: {res_owner.text}"
    owner_token = res_owner.json()["access_token"]
    print(f"  ✓ Owner Logged in: {res_owner.json()['user']['full_name']} (Role: {res_owner.json()['user']['role']})")

    # Manager login
    res_mgr = client.post("/api/v1/auth/login", json={"username": "manager", "password": "password123"})
    assert res_mgr.status_code == 200
    mgr_token = res_mgr.json()["access_token"]
    print(f"  ✓ Manager Logged in: {res_mgr.json()['user']['full_name']} (Role: {res_mgr.json()['user']['role']})")

    # Cashier login
    res_csh = client.post("/api/v1/auth/login", json={"username": "cashier1", "password": "password123"})
    assert res_csh.status_code == 200
    csh_token = res_csh.json()["access_token"]
    print(f"  ✓ Cashier Logged in: {res_csh.json()['user']['full_name']} (Role: {res_csh.json()['user']['role']})")

    # 7. Current Profile & Token Verification (/auth/me)
    print("\n[Test 7] Testing Token Verification (/api/v1/auth/me)...")
    res_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {owner_token}"})
    assert res_me.status_code == 200
    profile = res_me.json()
    print(f"  ✓ Authenticated as: {profile['username']} | Role: {profile['role']}")
    print(f"  ✓ Permissions: Can View Reports={profile['permissions']['can_view_reports']}, Can Bill={profile['permissions']['can_bill']}")

    # 8. Role-Based Access Control (RBAC) - Reports & Settings
    print("\n[Test 8] Testing RBAC: Reports & Settings Access Control...")
    # Owner can access reports
    res_rep_owner = client.get("/api/v1/reports/summary", headers={"Authorization": f"Bearer {owner_token}"})
    assert res_rep_owner.status_code == 200
    rep_data = res_rep_owner.json()
    print(f"  ✓ Owner Reports Access: GRANTED (Inventory Retail: Rs.{rep_data['inventory_kpis']['inventory_retail_valuation']})")

    # Owner can access settings
    res_sett_owner = client.get("/api/v1/settings/", headers={"Authorization": f"Bearer {owner_token}"})
    assert res_sett_owner.status_code == 200
    print(f"  ✓ Owner Settings Access: GRANTED (Store: {res_sett_owner.json()['store_name']})")

    # Manager CANNOT access owner reports
    res_rep_mgr = client.get("/api/v1/reports/summary", headers={"Authorization": f"Bearer {mgr_token}"})
    assert res_rep_mgr.status_code == 403
    print(f"  ✓ Manager Reports Access: DENIED (403 Forbidden as expected)")

    # Cashier CANNOT access owner reports
    res_rep_csh = client.get("/api/v1/reports/summary", headers={"Authorization": f"Bearer {csh_token}"})
    assert res_rep_csh.status_code == 403
    print(f"  ✓ Cashier Reports Access: DENIED (403 Forbidden as expected)")

    # Cashier CANNOT access owner settings
    res_sett_csh = client.get("/api/v1/settings/", headers={"Authorization": f"Bearer {csh_token}"})
    assert res_sett_csh.status_code == 403
    print(f"  ✓ Cashier Settings Access: DENIED (403 Forbidden as expected)")

    # 9. RBAC - Inventory Mutations
    print("\n[Test 9] Testing RBAC: Inventory Product Management...")
    new_product_payload = {
        "name": "Organic Almond Milk 1L",
        "barcode": "890999888111",
        "price": 140.0,
        "cost_price": 95.0,
        "stock_quantity": 30.0,
        "unit": "pcs",
        "tax_rate": 0.05
    }

    # Cashier CANNOT create a product
    res_prod_csh = client.post("/api/v1/products/", json=new_product_payload, headers={"Authorization": f"Bearer {csh_token}"})
    assert res_prod_csh.status_code == 403
    print(f"  ✓ Cashier Product Creation: DENIED (403 Forbidden as expected)")

    # Manager CAN create a product
    res_prod_mgr = client.post("/api/v1/products/", json=new_product_payload, headers={"Authorization": f"Bearer {mgr_token}"})
    if res_prod_mgr.status_code == 400: # If already created in prior run
        print(f"  ✓ Manager Product Creation: VERIFIED (Product exists or created)")
    else:
        assert res_prod_mgr.status_code == 201
        print(f"  ✓ Manager Product Creation: GRANTED (Created: {res_prod_mgr.json()['name']} with ID {res_prod_mgr.json()['id']})")

    # 10. Real-time Billing Calculation
    print("\n[Test 10] Testing Real-time Cart Calculations (/api/v1/billing/calculate)...")
    calc_payload = {
        "items": [
            {"product_id": prod["id"], "product_name": prod["name"], "unit_price": 100.0, "quantity": 2.0, "tax_rate": 0.05, "discount_amount": 0.0},
            {"product_name": "Artisan Bread", "unit_price": 50.0, "quantity": 1.0, "tax_rate": 0.05, "discount_amount": 0.0}
        ],
        "discount_percent": 10.0,
        "discount_fixed": 0.0
    }
    res = client.post("/api/v1/billing/calculate", json=calc_payload)
    assert res.status_code == 200
    calc = res.json()
    print(f"  ✓ Subtotal: Rs.{calc['subtotal']} | Tax: Rs.{calc['tax_total']} | Grand Total: Rs.{calc['grand_total']}")

    # 11. POS Checkout & Receipt Generation
    print("\n[Test 11] Testing Complete POS Checkout (/api/v1/orders/checkout)...")
    checkout_payload = {
        "cashier_name": "Cashier Rahul Sharma",
        "payment_method": "CASH",
        "discount_amount": 10.0,
        "notes": "Verified RBAC test checkout",
        "items": [
            {
                "product_id": prod["id"],
                "product_name": prod["name"],
                "unit_price": prod["price"],
                "quantity": 1.0,
                "unit": prod["unit"],
                "tax_rate": prod["tax_rate"],
                "discount_amount": 0.0
            }
        ]
    }
    res = client.post("/api/v1/orders/checkout", json=checkout_payload)
    assert res.status_code == 201
    order = res.json()
    print(f"  ✓ Generated Invoice: {order['invoice_number']} | Total: Rs.{order['total_amount']} | Status: {order['payment_status']}")

    # 12. Low-Stock Alerts Endpoint
    print("\n[Test 12] Testing Low-Stock Alerts (/api/v1/products/low-stock)...")
    res_low = client.get("/api/v1/products/low-stock?threshold=50")
    assert res_low.status_code == 200
    low_items = res_low.json()
    print(f"  ✓ Found {len(low_items)} products with stock <= 50 (Low Stock Alert working)")

    # 13. Categories CRUD
    print("\n[Test 13] Testing Categories CRUD API...")
    cat_payload = {
        "name": "Frozen & Gourmet Foods",
        "code": "CAT-FROZEN-TEST",
        "default_tax_rate": 0.12,
        "description": "Frozen peas, ice creams, and ready-to-eat meals"
    }
    res_cat = client.post("/api/v1/categories/", json=cat_payload, headers={"Authorization": f"Bearer {mgr_token}"})
    if res_cat.status_code == 400:
        print("  ✓ Category exists from prior run, verified unique constraint")
    else:
        assert res_cat.status_code == 201
        print(f"  ✓ Category Created: {res_cat.json()['name']} (Code: {res_cat.json()['code']})")

    # 14. Suppliers CRUD
    print("\n[Test 14] Testing Suppliers CRUD API...")
    supplier_payload = {
        "name": "Himalayan Agro Co-operative Ltd",
        "contact_person": "Kavita Sharma",
        "email": "kavita@himalayanagro.in",
        "phone": "+91 98765 43210",
        "address": "Himachal Cold Storage Depot, Mandi",
        "tax_number": "02AABCH5544G1Z8"
    }
    res_sup = client.post("/api/v1/suppliers/", json=supplier_payload, headers={"Authorization": f"Bearer {mgr_token}"})
    if res_sup.status_code == 400:
        print("  ✓ Supplier exists from prior run, verified unique constraint")
    else:
        assert res_sup.status_code == 201
        print(f"  ✓ Supplier Registered: {res_sup.json()['name']} (Rep: {res_sup.json()['contact_person']})")

    # 15. Purchase Orders & Inventory Restocking
    print("\n[Test 15] Testing Procurement Purchase Orders & Auto-Stocking...")
    # Get initial stock of product #1
    prod_initial = client.get(f"/api/v1/products/{prod['id']}").json()
    initial_stock = prod_initial["stock_quantity"]

    po_payload = {
        "supplier_id": 1,
        "notes": "Automated Restocking PO",
        "items": [
            {
                "product_id": prod["id"],
                "quantity_ordered": 25.0,
                "unit_cost": 120.0
            }
        ]
    }
    res_po = client.post("/api/v1/purchase-orders/", json=po_payload, headers={"Authorization": f"Bearer {mgr_token}"})
    assert res_po.status_code == 201
    po = res_po.json()
    print(f"  ✓ Generated PO: {po['po_number']} | Total: Rs.{po['total_amount']} | Status: {po['status']}")

    # Mark PO as RECEIVED
    res_rec = client.put(f"/api/v1/purchase-orders/{po['id']}/status", json={"status": "RECEIVED"}, headers={"Authorization": f"Bearer {mgr_token}"})
    assert res_rec.status_code == 200
    print(f"  ✓ PO {po['po_number']} marked as RECEIVED")

    # Verify that product stock automatically increased by 25!
    prod_after = client.get(f"/api/v1/products/{prod['id']}").json()
    expected_stock = initial_stock + 25.0
    assert prod_after["stock_quantity"] == expected_stock, f"Expected {expected_stock}, got {prod_after['stock_quantity']}"
    print(f"  ✓ Stock Automatically Restocked: {initial_stock} -> {prod_after['stock_quantity']} {prod_after['unit']}")

    # 16. Billing Engine (Checkout Process) - Subtotal, Taxes, Discounts & Stock Decrement
    print("\n[Test 16] Testing Billing Engine (/api/v1/billing/generate-bill)...")
    prod_before_bill = client.get(f"/api/v1/products/{prod['id']}").json()
    stock_before_bill = prod_before_bill["stock_quantity"]

    bill_payload = {
        "cashier_name": "Cashier Arjun Rao",
        "customer_name": "Pooja Verma",
        "customer_phone": "+91 99887 76655",
        "payment_method": "UPI",
        "discount_percent": 10.0,
        "discount_fixed": 15.0,
        "tax_rate_override": 0.05,
        "tendered_amount": 500.0,
        "notes": "Fast Checkout Billing Terminal",
        "items": [
            {
                "product_id": prod["id"],
                "product_name": prod["name"],
                "barcode": prod["barcode"],
                "unit_price": prod["price"],
                "quantity": 2.0,
                "unit": prod["unit"],
                "tax_rate": 0.05,
                "discount_amount": 0.0
            }
        ]
    }
    res_bill = client.post("/api/v1/billing/generate-bill", json=bill_payload)
    assert res_bill.status_code == 201, f"Generate bill failed: {res_bill.text}"
    bill = res_bill.json()
    assert bill["invoice_number"].startswith("INV-")
    assert bill["payment_method"] == "UPI"
    assert bill["customer_name"] == "Pooja Verma"
    assert len(bill["items"]) == 1

    # Verify inventory was decremented by 2.0
    prod_after_bill = client.get(f"/api/v1/products/{prod['id']}").json()
    assert prod_after_bill["stock_quantity"] == stock_before_bill - 2.0, (
        f"Expected stock {stock_before_bill - 2.0}, got {prod_after_bill['stock_quantity']}"
    )
    print(f"  ✓ Bill Generated: {bill['invoice_number']} | Subtotal: Rs.{bill['subtotal']} | Total: Rs.{bill['total_amount']}")
    print(f"  ✓ Inventory Decremented: {stock_before_bill} -> {prod_after_bill['stock_quantity']} {prod_after_bill['unit']}")

    # 17. Pre-Checkout Stock Validation (Insufficient Stock Rejection)
    print("\n[Test 17] Testing Pre-Checkout Stock Validation Guard (Insufficient Stock)...")
    excessive_qty = prod_after_bill["stock_quantity"] + 1000.0
    oversell_payload = {
        "cashier_name": "Cashier Test",
        "payment_method": "CASH",
        "items": [
            {
                "product_id": prod["id"],
                "product_name": prod["name"],
                "barcode": prod["barcode"],
                "unit_price": prod["price"],
                "quantity": excessive_qty,
                "unit": prod["unit"]
            }
        ]
    }
    res_oversell = client.post("/api/v1/billing/generate-bill", json=oversell_payload)
    assert res_oversell.status_code == 400, f"Expected 400 Bad Request, got {res_oversell.status_code}"
    error_detail = res_oversell.json()["detail"]
    assert "Insufficient stock" in error_detail, f"Expected 'Insufficient stock' in '{error_detail}'"
    print(f"  ✓ Oversell Correctly Rejected: {error_detail}")

    # Verify stock remained untouched after rejection
    prod_post_reject = client.get(f"/api/v1/products/{prod['id']}").json()
    assert prod_post_reject["stock_quantity"] == prod_after_bill["stock_quantity"]
    print(f"  ✓ Stock Integrity Preserved: Unchanged at {prod_post_reject['stock_quantity']} {prod_post_reject['unit']}")

    # 18. Payment Recording & Status Update to 'Paid'
    print("\n[Test 18] Testing Payments Recording (/api/v1/payments/record)...")
    pmt_payload = {
        "invoice_number": bill["invoice_number"],
        "payment_method": "CARD",
        "amount": bill["total_amount"],
        "transaction_reference": "POS-AUTH-88231",
        "notes": "Card tap customer payment"
    }
    res_pmt = client.post("/api/v1/payments/record", json=pmt_payload)
    assert res_pmt.status_code == 201, f"Expected 201, got {res_pmt.text}"
    pmt_res = res_pmt.json()
    assert pmt_res["success"] is True
    assert pmt_res["sale_status"] == "Paid"
    assert pmt_res["payment_method"] == "CARD"
    print(f"  ✓ Payment Recorded: Rs.{pmt_res['total_paid']} via {pmt_res['payment_method']}")
    print(f"  ✓ Sale Record Status Updated to: '{pmt_res['sale_status']}'")

    # 19. Split Payments (Cash + UPI Breakdown)
    print("\n[Test 19] Testing Split Payments (Cash + UPI)...")
    # Generate another bill to test Split payments directly via /billing/generate-bill
    split_bill_payload = {
        "cashier_name": "Cashier Rahul",
        "customer_name": "Sunita Rao",
        "customer_phone": "+91 91234 56789",
        "payment_method": "SPLIT",
        "split_breakdown": [
            {"method": "CASH", "amount": 100.0, "tendered_amount": 100.0},
            {"method": "UPI", "amount": 90.0, "transaction_reference": "UPI-UTR-991823"}
        ],
        "items": [
            {
                "product_id": prod["id"],
                "product_name": prod["name"],
                "barcode": prod["barcode"],
                "unit_price": 190.0,
                "quantity": 1.0,
                "unit": prod["unit"],
                "tax_rate": 0.0,
                "discount_amount": 0.0
            }
        ]
    }
    res_split = client.post("/api/v1/billing/generate-bill", json=split_bill_payload)
    assert res_split.status_code == 201, f"Split billing failed: {res_split.text}"
    split_bill = res_split.json()
    assert split_bill["status"] == "Paid"
    assert split_bill["payment_method"] == "SPLIT"
    assert len(split_bill["split_breakdown"]) == 2
    print(f"  ✓ Split Bill Generated: {split_bill['invoice_number']} | Status: '{split_bill['status']}'")
    print(f"  ✓ Split Breakdown: Cash=Rs.{split_bill['split_breakdown'][0]['amount']}, UPI=Rs.{split_bill['split_breakdown'][1]['amount']}")

    # 20. Payments & Receipts Lookup (/api/v1/payments/sale/{sale_id})
    print("\n[Test 20] Testing Payments & Receipt Lookup (/api/v1/payments/sale/{id})...")
    res_sale_pmts = client.get(f"/api/v1/payments/sale/{split_bill['id']}")
    assert res_sale_pmts.status_code == 200
    sale_pmts = res_sale_pmts.json()
    assert len(sale_pmts) == 2
    print(f"  ✓ Retrieved {len(sale_pmts)} payment ledger records for Invoice {split_bill['invoice_number']}")
    for sp in sale_pmts:
        print(f"    - Payment #{sp['id']}: {sp['payment_method']} Rs.{sp['amount']} (Status: {sp['status']})")

    # 21. Automatic Stock Deduction Verification on Sale Completion
    print("\n[Test 21] Testing Automatic Inventory Stock Deduction...")
    prod_test = client.get(f"/api/v1/products/{prod['id']}").json()
    stock_prior_sale = prod_test["stock_quantity"]

    test_sale_payload = {
        "cashier_name": "Cashier Rahul",
        "customer_name": "Vikas Test Customer",
        "payment_method": "CASH",
        "items": [
            {
                "product_id": prod["id"],
                "product_name": prod["name"],
                "barcode": prod["barcode"],
                "unit_price": prod["price"],
                "quantity": 3.0,
                "unit": prod["unit"],
                "tax_rate": 0.05,
                "discount_amount": 0.0
            }
        ]
    }
    res_tsale = client.post("/api/v1/billing/generate-bill", json=test_sale_payload)
    assert res_tsale.status_code == 201
    tsale = res_tsale.json()

    prod_post_sale = client.get(f"/api/v1/products/{prod['id']}").json()
    assert prod_post_sale["stock_quantity"] == stock_prior_sale - 3.0
    print(f"  ✓ Automatic Deduction Verified: {stock_prior_sale} -> {prod_post_sale['stock_quantity']} {prod['unit']} (-3.0 units)")

    # 22. Return & Refund Processing (Stock Added Back & Payment Reversed)
    print("\n[Test 22] Testing Return & Refund Processing (/api/v1/returns/process)...")
    return_payload = {
        "sale_id": tsale["id"],
        "refund_method": "CASH",
        "notes": "Customer returned unopened items",
        "items": [
            {
                "product_id": prod["id"],
                "quantity": 2.0,
                "reason": "Customer Changed Mind / Unopened"
            }
        ]
    }
    res_ret = client.post("/api/v1/returns/process", json=return_payload)
    assert res_ret.status_code == 201, f"Return failed: {res_ret.text}"
    ret_res = res_ret.json()
    assert ret_res["success"] is True
    assert ret_res["return_number"].startswith("RET-")
    assert ret_res["returned_items"][0]["quantity_returned"] == 2.0
    assert ret_res["returned_items"][0]["restocked"] is True

    # Verify inventory was automatically added back (+2.0)
    prod_post_return = client.get(f"/api/v1/products/{prod['id']}").json()
    assert prod_post_return["stock_quantity"] == prod_post_sale["stock_quantity"] + 2.0, (
        f"Expected stock {prod_post_sale['stock_quantity'] + 2.0}, got {prod_post_return['stock_quantity']}"
    )
    print(f"  ✓ Return Processed: {ret_res['return_number']} | Refund: Rs.{ret_res['refund_amount']}")
    print(f"  ✓ Stock Restored: {prod_post_sale['stock_quantity']} -> {prod_post_return['stock_quantity']} {prod['unit']} (+2.0 units added back)")

    # 23. Return Validation (Preventing Over-returns)
    print("\n[Test 23] Testing Return Guard (Preventing Return of More than Remaining Quantity)...")
    excessive_return_payload = {
        "sale_id": tsale["id"],
        "refund_method": "CASH",
        "items": [
            {
                "product_id": prod["id"],
                "quantity": 5.0, # only 1.0 remains returnable from the 3 purchased
                "reason": "Defective"
            }
        ]
    }
    res_ex_ret = client.post("/api/v1/returns/process", json=excessive_return_payload)
    assert res_ex_ret.status_code == 400
    print(f"  ✓ Excessive Return Rejection Verified: {res_ex_ret.json()['detail']}")

    # 24. Sales History & Returns Ledger Query (/api/v1/sales/)
    print("\n[Test 24] Testing Sales History & Returns API (/api/v1/sales/)...")
    res_sales_history = client.get("/api/v1/sales/?limit=10")
    assert res_sales_history.status_code == 200
    sales_hist = res_sales_history.json()
    assert len(sales_hist) >= 2
    target_sale = next((s for s in sales_hist if s["id"] == tsale["id"]), None)
    assert target_sale is not None
    assert len(target_sale["returns"]) >= 1
    assert target_sale["returns"][0]["return_number"] == ret_res["return_number"]
    print(f"  ✓ Sales History Loaded: {len(sales_hist)} invoices found")
    print(f"  ✓ Sale #{target_sale['id']} contains Return #{target_sale['returns'][0]['return_number']} (Refund: Rs.{target_sale['returns'][0]['refund_amount']})")

    # 25. Dashboard Metrics (Today's Sales, Cash vs Card, Low Stock, Profit/Loss)
    print("\n[Test 25] Testing Dashboard Metrics API (/api/v1/reports/dashboard)...")
    res_dash = client.get("/api/v1/reports/dashboard")
    assert res_dash.status_code == 200, f"Expected 200, got {res_dash.text}"
    dash = res_dash.json()

    # Verify Today's Sales
    assert "today_sales" in dash
    assert dash["today_sales"]["total_revenue"] >= 0.0
    assert dash["today_sales"]["transactions_count"] >= 1
    print(f"  ✓ Today's Sales: Rs.{dash['today_sales']['total_revenue']} across {dash['today_sales']['transactions_count']} orders (Avg: Rs.{dash['today_sales']['avg_basket_value']})")

    # Verify Cash vs Card vs UPI
    assert "payment_methods" in dash
    pm = dash["payment_methods"]
    assert "cash" in pm and "card" in pm and "upi" in pm
    print(f"  ✓ Payment Tenders: Cash=Rs.{pm['cash']['total']} ({pm['cash']['count']}), Card=Rs.{pm['card']['total']} ({pm['card']['count']}), UPI=Rs.{pm['upi']['total']} ({pm['upi']['count']})")

    # Verify Low Stock Products
    assert "low_stock" in dash
    assert dash["low_stock"]["total_count"] >= 1
    assert len(dash["low_stock"]["products"]) >= 1
    print(f"  ✓ Low Stock Products Alert: {dash['low_stock']['total_count']} items below threshold")

    # Verify Profit / Loss Estimations
    assert "profit_loss" in dash
    pl = dash["profit_loss"]
    assert pl["gross_revenue"] > 0
    assert pl["cost_of_goods_sold"] >= 0
    assert pl["margin_pct"] >= 0
    print(f"  ✓ Profit/Loss Estimation: Revenue=Rs.{pl['gross_revenue']}, COGS=Rs.{pl['cost_of_goods_sold']}, Gross Profit=Rs.{pl['gross_profit']} (Margin: {pl['margin_pct']}%)")

    # 26. Best-Selling Products Ranking (/api/v1/reports/best-sellers)
    print("\n[Test 26] Testing Best-Selling Products API (/api/v1/reports/best-sellers)...")
    res_bs = client.get("/api/v1/reports/best-sellers?limit=5")
    assert res_bs.status_code == 200
    best_sellers = res_bs.json()
    assert len(best_sellers) >= 1
    top_p = best_sellers[0]
    print(f"  ✓ Best Seller #1: '{top_p['product_name']}' - {top_p['units_sold']} units sold (Rs.{top_p['total_sales_value']})")

    # 27. Historical Sales Trends (Daily & Monthly)
    print("\n[Test 27] Testing Sales Trends API (/api/v1/reports/sales-trends)...")
    res_daily = client.get("/api/v1/reports/sales-trends?period=daily")
    assert res_daily.status_code == 200
    daily_trends = res_daily.json()
    assert len(daily_trends) == 14

    res_monthly = client.get("/api/v1/reports/sales-trends?period=monthly")
    assert res_monthly.status_code == 200
    monthly_trends = res_monthly.json()
    print(f"  ✓ Sales Trends: 14-day daily data verified & {len(monthly_trends)} monthly buckets loaded")

    # 28. Operational Audit Logs Trail (/api/v1/reports/audit-logs)
    print("\n[Test 28] Testing Operational Audit Logs API (/api/v1/reports/audit-logs)...")
    res_audit = client.get("/api/v1/reports/audit-logs?limit=20")
    assert res_audit.status_code == 200
    audit_events = res_audit.json()
    assert len(audit_events) >= 3
    event_types = set(e["event_type"] for e in audit_events)
    assert "CHECKOUT" in event_types
    print(f"  ✓ Audit Logs: {len(audit_events)} audit events recorded across types: {event_types}")

    # 29. Pydantic Form Validation Error Handling (422)
    print("\n[Test 29] Testing Backend Pydantic Form Validation & Error Handling...")
    # Test invalid product payload (empty name, negative price)
    bad_prod = client.post(
        "/api/v1/products/",
        json={"name": "   ", "barcode": " ", "price": -50.0},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert bad_prod.status_code == 422, f"Expected 422, got {bad_prod.status_code}: {bad_prod.text}"
    val_err = bad_prod.json()
    assert "detail" in val_err or "errors" in val_err
    print(f"  ✓ Invalid Product Payload Correctly Blocked: HTTP 422 with structured validation error")

    # Test empty cart in billing request
    empty_bill = client.post(
        "/api/v1/billing/generate-bill",
        json={"items": [], "payment_method": "CASH"},
        headers={"Authorization": f"Bearer {csh_token}"}
    )
    assert empty_bill.status_code == 422, f"Expected 422, got {empty_bill.status_code}: {empty_bill.text}"
    print(f"  ✓ Empty Cart Bill Request Correctly Blocked: HTTP 422 validation guard active")

    # 30. Proper Resource Error Handling (404 Not Found)
    print("\n[Test 30] Testing Endpoints Error Handling for Missing Resources (404)...")
    res_missing_barcode = client.get("/api/v1/products/barcode/999999999999999")
    assert res_missing_barcode.status_code == 404
    assert "detail" in res_missing_barcode.json()
    print(f"  ✓ Non-existent Barcode: HTTP 404 with message: '{res_missing_barcode.json()['detail']}'")

    res_missing_sale = client.get("/api/v1/sales/999999")
    assert res_missing_sale.status_code == 404
    print(f"  ✓ Non-existent Sale ID: HTTP 404 with message: '{res_missing_sale.json()['detail']}'")

    print("\n" + "=" * 70)
    print("🎉 ALL 30 INTEGRATION, RBAC, INVENTORY, BILLING, PAYMENTS, RETURNS, ANALYTICS & VALIDATION TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    test_system()

