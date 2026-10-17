"""Comprehensive Database Seeder for Grocery POS System.
Seeds:
- Default Users with roles (Owner, Manager, Cashier)
- Suppliers (Procurement distributors)
- Departments/Categories with tax rates
- Over 520 realistic grocery products with unique barcodes, pricing, costs, stock levels, and expiry dates.
"""

import sys
import os
from datetime import datetime, date, timedelta
import random

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure app is discoverable
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.payment import Payment
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.customer import Customer
from app.core.security import hash_secret

def seed_database():
    print("=" * 65)
    print("[POS SEED] Starting Grocery POS Database Seeding (500+ Items)...")
    print("=" * 65)

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Users
        print("\n[1/4] Seeding Users (Owner, Manager, Cashier)...")
        existing_users = {u.username: u for u in db.query(User).all()}
        users_data = [
            {"username": "owner", "email": "owner@grocerypos.com", "full_name": "Vikas Store Owner", "password": "password123", "role": UserRole.OWNER, "phone": "+91 98200 00001"},
            {"username": "manager", "email": "manager@grocerypos.com", "full_name": "Amit Kumar Manager", "password": "password123", "role": UserRole.MANAGER, "phone": "+91 98200 00002"},
            {"username": "cashier1", "email": "cashier1@grocerypos.com", "full_name": "Rahul Sharma (Terminal 1)", "password": "password123", "role": UserRole.CASHIER, "phone": "+91 98200 00003"},
            {"username": "cashier2", "email": "cashier2@grocerypos.com", "full_name": "Pooja Verma (Terminal 2)", "password": "password123", "role": UserRole.CASHIER, "phone": "+91 98200 00004"},
        ]

        seeded_users = {}
        for u in users_data:
            if u["username"] not in existing_users:
                user_obj = User(
                    username=u["username"],
                    email=u["email"],
                    full_name=u["full_name"],
                    hashed_password=hash_secret(u["password"]),
                    role=u["role"],
                    phone=u["phone"],
                    is_active=True,
                )
                db.add(user_obj)
                seeded_users[u["username"]] = user_obj
            else:
                seeded_users[u["username"]] = existing_users[u["username"]]
        db.commit()
        print(f"[OK] Users ready: {len(users_data)} users verified.")

        # 2. Seed Suppliers
        print("\n[2/4] Seeding Suppliers...")
        existing_suppliers = {s.name: s for s in db.query(Supplier).all()}
        suppliers_data = [
            {"name": "Metro Wholesale Agrotech", "contact_person": "Sunil Gupta", "email": "supply@metrowholesale.in", "phone": "+91 98111 22334", "address": "Yard 4, APMC Market, Vashi", "tax_number": "27AABCM1234F1Z1"},
            {"name": "Amul Anand Dairy Cooperative", "contact_person": "Ramesh Patel", "email": "distrib@amul.coop", "phone": "+91 98222 33445", "address": "Amul Dairy Road, Anand, Gujarat", "tax_number": "24AAACA1122B1Z3"},
            {"name": "Fresh Farms Organic Produce Ltd", "contact_person": "Sanjay Deshmukh", "email": "orders@freshfarms.in", "phone": "+91 98333 44556", "address": "Plot 12, Nashik Agro Hub", "tax_number": "27AAACF9988C1Z8"},
            {"name": "Hindustan FMCG Mega Distributors", "contact_person": "Vikram Mehta", "email": "orders@hulfmcg.com", "phone": "+91 98444 55667", "address": "Bhiwandi Warehousing Complex", "tax_number": "27AAACH4455D1Z5"},
            {"name": "Heritage Millers & Grains Corp", "contact_person": "Harpreet Singh", "email": "sales@herigrains.in", "phone": "+91 98555 66778", "address": "Grain Market, Karnal, Haryana", "tax_number": "06AAACH7788E1Z9"},
        ]

        seeded_suppliers = {}
        for s in suppliers_data:
            if s["name"] not in existing_suppliers:
                supp = Supplier(**s)
                db.add(supp)
                db.flush()
                seeded_suppliers[s["name"]] = supp
            else:
                seeded_suppliers[s["name"]] = existing_suppliers[s["name"]]
        db.commit()
        print(f"[OK] Suppliers ready: {len(suppliers_data)} suppliers verified.")

        # 3. Seed Categories
        print("\n[3/4] Seeding Categories...")
        existing_categories = {c.name: c for c in db.query(Category).all()}
        categories_data = [
            {"name": "Fresh Fruits", "code": "CAT-FRUITS", "icon": "fruits", "default_tax_rate": 0.00, "description": "Fresh seasonal and imported farm fruits"},
            {"name": "Fresh Vegetables", "code": "CAT-VEG", "icon": "veg", "default_tax_rate": 0.00, "description": "Green vegetables, roots, gourds and fresh herbs"},
            {"name": "Dairy & Eggs", "code": "CAT-DAIRY", "icon": "dairy", "default_tax_rate": 0.05, "description": "Fresh milk, paneer, butter, cheese, curd and farm eggs"},
            {"name": "Bakery & Breads", "code": "CAT-BAKERY", "icon": "bakery", "default_tax_rate": 0.05, "description": "Freshly baked artisan bread, buns, toast and rolls"},
            {"name": "Rice & Flours", "code": "CAT-GRAINS", "icon": "grains", "default_tax_rate": 0.05, "description": "Basmati rice, whole wheat atta, maida, and rava"},
            {"name": "Pulses & Dals", "code": "CAT-PULSES", "icon": "pulses", "default_tax_rate": 0.00, "description": "Lentils, toor dal, moong, chana, rajma and legumes"},
            {"name": "Cooking Oils & Ghee", "code": "CAT-OILS", "icon": "oils", "default_tax_rate": 0.05, "description": "Edible cooking oils, pure desi ghee and vanaspati"},
            {"name": "Spices & Seasonings", "code": "CAT-SPICES", "icon": "spices", "default_tax_rate": 0.05, "description": "Whole spices, powdered masalas, salt and jaggery"},
            {"name": "Beverages & Tea", "code": "CAT-BEV", "icon": "bev", "default_tax_rate": 0.12, "description": "Premium tea blends, roast coffee, juices and soft drinks"},
            {"name": "Snacks & Biscuits", "code": "CAT-SNACKS", "icon": "snacks", "default_tax_rate": 0.18, "description": "Cookies, chips, savory namkeen, pasta and chocolates"},
            {"name": "Cleaning & Household", "code": "CAT-HOUSEHOLD", "icon": "cleaning", "default_tax_rate": 0.18, "description": "Detergents, floor cleaners, dishwash and foils"},
            {"name": "Personal Care", "code": "CAT-CARE", "icon": "care", "default_tax_rate": 0.18, "description": "Soaps, body washes, oral hygiene and shampoos"},
        ]

        seeded_categories = {}
        for c in categories_data:
            if c["name"] not in existing_categories:
                cat = Category(**c)
                db.add(cat)
                db.flush()
                seeded_categories[c["name"]] = cat
            else:
                seeded_categories[c["name"]] = existing_categories[c["name"]]
        db.commit()
        print(f"[OK] Categories ready: {len(categories_data)} categories verified.")

        # 4. Seed 500+ Grocery Products
        print("\n[4/4] Generating 500+ Grocery Products...")
        existing_barcodes = {p.barcode for p in db.query(Product.barcode).all()}

        catalog_raw = []

        fruits = [
            ("Royal Gala Apples", 190.0, 140.0, "kg", 0.0, 30),
            ("Granny Smith Green Apples", 240.0, 180.0, "kg", 0.0, 35),
            ("Washington Red Delicious Apples", 210.0, 155.0, "kg", 0.0, 30),
            ("Shimla Kinnaur Apples", 160.0, 115.0, "kg", 0.0, 25),
            ("Fuji Sweet Apples", 220.0, 165.0, "kg", 0.0, 35),
            ("Honeycrisp Apples", 260.0, 195.0, "kg", 0.0, 28),
            ("Cavendish Banana Premium", 55.0, 38.0, "kg", 0.0, 7),
            ("Robusta Bananas", 45.0, 30.0, "kg", 0.0, 6),
            ("Elaichi Small Sweet Bananas", 80.0, 55.0, "kg", 0.0, 5),
            ("Red Banana Kerala", 95.0, 70.0, "kg", 0.0, 7),
            ("Nagpur Sweet Oranges", 85.0, 60.0, "kg", 0.0, 15),
            ("Mosambi (Sweet Lime)", 75.0, 50.0, "kg", 0.0, 12),
            ("Valencia Imported Oranges", 140.0, 100.0, "kg", 0.0, 20),
            ("Nagpur Mandarin Oranges", 90.0, 65.0, "kg", 0.0, 14),
            ("Kinnow Juicy Oranges", 65.0, 45.0, "kg", 0.0, 18),
            ("Ruby Grapefruit", 180.0, 130.0, "kg", 0.0, 25),
            ("Alphonso Mango Ratnagiri (Dozen)", 750.0, 550.0, "pack", 0.0, 10),
            ("Kesar Mango Gujarat", 280.0, 200.0, "kg", 0.0, 12),
            ("Banganapalli Sweet Mango", 140.0, 95.0, "kg", 0.0, 10),
            ("Dasheri Mango Malihabad", 160.0, 110.0, "kg", 0.0, 10),
            ("Langra Green Mango", 150.0, 105.0, "kg", 0.0, 8),
            ("Totapuri Mango", 80.0, 55.0, "kg", 0.0, 14),
            ("Papaya Semi-Ripe Sweet 1kg", 55.0, 35.0, "pcs", 0.0, 7),
            ("Queen Pineapple Sweet 1pc", 85.0, 55.0, "pcs", 0.0, 10),
            ("Watermelon Kiran Striped 2.5kg", 90.0, 55.0, "pcs", 0.0, 14),
            ("Muskmelon Madhumati 1kg", 65.0, 40.0, "pcs", 0.0, 9),
            ("Ruby Red Pomegranate 1kg", 220.0, 160.0, "kg", 0.0, 21),
            ("Thai Guava White Sweet", 110.0, 75.0, "kg", 0.0, 10),
            ("Pink Guava Local", 80.0, 50.0, "kg", 0.0, 7),
            ("Thompson Seedless Green Grapes 500g", 85.0, 58.0, "pack", 0.0, 10),
            ("Sonaka Long Seedless Grapes 500g", 95.0, 65.0, "pack", 0.0, 10),
            ("Black Seedless Grapes Sharad 500g", 110.0, 78.0, "pack", 0.0, 10),
            ("Red Globe Large Grapes 500g", 160.0, 115.0, "pack", 0.0, 12),
            ("Mahabaleshwar Fresh Strawberries 200g", 80.0, 55.0, "pack", 0.0, 5),
            ("Imported Blueberries 125g", 240.0, 180.0, "pack", 0.0, 14),
            ("Fresh Blackberries 125g", 280.0, 210.0, "pack", 0.0, 10),
            ("Fresh Raspberries 125g", 290.0, 220.0, "pack", 0.0, 8),
            ("Red Dragon Fruit 1pc", 110.0, 75.0, "pcs", 0.0, 18),
            ("White Flesh Dragon Fruit 1pc", 95.0, 65.0, "pcs", 0.0, 18),
            ("Zespri Green Kiwi (Pack of 3)", 125.0, 85.0, "pack", 0.0, 20),
            ("Zespri Gold Sweet Kiwi (Pack of 3)", 180.0, 130.0, "pack", 0.0, 20),
            ("Avocado Hass Imported (Pack of 2)", 240.0, 175.0, "pack", 0.0, 12),
            ("Indian Butter Fruit Avocado 1kg", 180.0, 120.0, "kg", 0.0, 10),
            ("Chikoo (Sapota) Dahanu 1kg", 75.0, 50.0, "kg", 0.0, 7),
            ("Custard Apple (Sitaphal) 1kg", 160.0, 110.0, "kg", 0.0, 6),
            ("Fresh Purple Figs (Anjeer) 250g", 90.0, 62.0, "pack", 0.0, 5),
            ("Nashik Green Pears 1kg", 140.0, 95.0, "kg", 0.0, 16),
            ("Imported Packham Pears 1kg", 220.0, 160.0, "kg", 0.0, 25),
            ("Black Amber Plums 500g", 140.0, 95.0, "pack", 0.0, 12),
            ("Kashmir Sweet Peaches 500g", 160.0, 110.0, "pack", 0.0, 9),
            ("Fresh Sweet Apricots 250g", 120.0, 85.0, "pack", 0.0, 10),
            ("Sweet Lychee Muzaffarpur 500g", 180.0, 125.0, "pack", 0.0, 6),
            ("De-husked Coconut Dry 1pc", 38.0, 25.0, "pcs", 0.0, 30),
            ("Green Tender Coconut 1pc", 55.0, 35.0, "pcs", 0.0, 10),
            ("Sweet Thai Tamarind Box 400g", 160.0, 115.0, "pack", 0.0, 90),
            ("Cape Gooseberries (Rasbhari) 250g", 70.0, 48.0, "pack", 0.0, 8),
            ("Fresh Amla (Indian Gooseberry) 500g", 45.0, 28.0, "pack", 0.0, 15),
            ("Passion Fruit Fresh (Pack of 4)", 150.0, 105.0, "pack", 0.0, 14),
            ("Sweet Cherries Box 250g", 280.0, 210.0, "pack", 0.0, 8),
            ("Fresh Medjool Dates 500g", 340.0, 250.0, "pack", 0.0, 120),
        ]
        catalog_raw.append(("Fresh Fruits", "Fresh Farms Organic Produce Ltd", "FRU", fruits))

        veg = [
            ("Country Red Tomatoes 1kg", 35.0, 22.0, "kg", 0.0, 7),
            ("Hybrid Salad Tomatoes 1kg", 45.0, 30.0, "kg", 0.0, 10),
            ("Cherry Tomatoes Pack 250g", 65.0, 42.0, "pack", 0.0, 12),
            ("Nashik Red Onions 1kg", 38.0, 25.0, "kg", 0.0, 25),
            ("Sambhar Small Shallots 500g", 55.0, 38.0, "pack", 0.0, 20),
            ("White Sweet Onions 1kg", 50.0, 32.0, "kg", 0.0, 20),
            ("Spring Onions Green (Bunch)", 25.0, 15.0, "pack", 0.0, 5),
            ("Potato Jyoti Agra 1kg", 32.0, 20.0, "kg", 0.0, 30),
            ("Baby Potatoes Small 500g", 30.0, 18.0, "pack", 0.0, 25),
            ("Sweet Potatoes Orange 1kg", 60.0, 40.0, "kg", 0.0, 20),
            ("Fresh White Garlic 250g", 65.0, 45.0, "pack", 0.0, 45),
            ("Ooty Special Big Garlic 250g", 85.0, 60.0, "pack", 0.0, 50),
            ("Fresh Ginger Rhizome 250g", 45.0, 28.0, "pack", 0.0, 20),
            ("Spicy Green Chillies 100g", 15.0, 8.0, "pack", 0.0, 10),
            ("Bhavnagri Mild Chillies 250g", 35.0, 22.0, "pack", 0.0, 10),
            ("Fresh Coriander Bunch 100g", 18.0, 8.0, "pack", 0.0, 4),
            ("Fresh Mint Leaves (Pudina) 100g", 15.0, 7.0, "pack", 0.0, 4),
            ("Spinach Leaves (Palak) 250g", 25.0, 14.0, "pack", 0.0, 4),
            ("Fresh Methi (Fenugreek) 250g", 28.0, 15.0, "pack", 0.0, 4),
            ("Shepu (Dill Leaves) Bunch", 20.0, 10.0, "pack", 0.0, 4),
            ("Curry Leaves Fresh (Kadi Patta) 50g", 10.0, 4.0, "pack", 0.0, 7),
            ("Cabbage Green Solid 1kg", 30.0, 18.0, "pcs", 0.0, 14),
            ("Red Ruby Cabbage 500g", 55.0, 35.0, "pcs", 0.0, 16),
            ("Fresh Cauliflower Head 1pc", 40.0, 24.0, "pcs", 0.0, 8),
            ("Exotic Green Broccoli 500g", 85.0, 55.0, "pcs", 0.0, 9),
            ("Button White Mushrooms 200g", 55.0, 36.0, "pack", 0.0, 6),
            ("Portobello Mushrooms 200g", 120.0, 80.0, "pack", 0.0, 6),
            ("Fresh Bottle Gourd (Lauki) 1kg", 35.0, 20.0, "pcs", 0.0, 8),
            ("Bitter Gourd (Karela) 500g", 35.0, 22.0, "pack", 0.0, 8),
            ("Ridge Gourd (Turai) 500g", 40.0, 25.0, "pack", 0.0, 7),
            ("Sponge Gourd (Ghilki) 500g", 38.0, 24.0, "pack", 0.0, 7),
            ("Snake Gourd 500g", 35.0, 22.0, "pack", 0.0, 7),
            ("Pointed Gourd (Parwal) 500g", 55.0, 36.0, "pack", 0.0, 8),
            ("Ivy Gourd (Tindora) 500g", 45.0, 28.0, "pack", 0.0, 9),
            ("Tender Okra (Bhindi) 500g", 40.0, 25.0, "pack", 0.0, 6),
            ("Cluster Beans (Gawar) 250g", 30.0, 18.0, "pack", 0.0, 6),
            ("French Fine Beans 250g", 35.0, 22.0, "pack", 0.0, 7),
            ("Broad Flat Beans (Sem) 500g", 45.0, 28.0, "pack", 0.0, 7),
            ("Fresh Green Peas (Matar) 1kg", 75.0, 48.0, "kg", 0.0, 8),
            ("Red English Carrots 1kg", 45.0, 28.0, "kg", 0.0, 15),
            ("Orange Local Carrots 1kg", 40.0, 24.0, "kg", 0.0, 12),
            ("White Mooli (Radish) 500g", 25.0, 14.0, "pack", 0.0, 8),
            ("Fresh Deep Red Beetroot 500g", 30.0, 18.0, "pack", 0.0, 15),
            ("English Salad Cucumber 500g", 35.0, 22.0, "pack", 0.0, 9),
            ("Country Crisp Cucumber 500g", 28.0, 16.0, "pack", 0.0, 8),
            ("Green Bell Pepper Capsicum 500g", 45.0, 28.0, "pack", 0.0, 10),
            ("Yellow Sweet Bell Pepper 250g", 75.0, 50.0, "pack", 0.0, 10),
            ("Red Sweet Bell Pepper 250g", 75.0, 50.0, "pack", 0.0, 10),
            ("Green Zucchini Squash 500g", 65.0, 42.0, "pack", 0.0, 9),
            ("Yellow Zucchini Squash 500g", 70.0, 46.0, "pack", 0.0, 9),
            ("Brinjal Bharta (Large Eggplant) 1kg", 45.0, 28.0, "kg", 0.0, 8),
            ("Small Purple Brinjal 500g", 30.0, 18.0, "pack", 0.0, 7),
            ("Green Round Brinjal 500g", 32.0, 20.0, "pack", 0.0, 7),
            ("Drumsticks (Moringa) 250g", 35.0, 22.0, "pack", 0.0, 8),
            ("Colocasia Root (Arbi) 500g", 40.0, 25.0, "pack", 0.0, 18),
            ("Raw Green Banana 500g", 30.0, 18.0, "pack", 0.0, 10),
            ("Raw Green Papaya 1kg", 40.0, 22.0, "pcs", 0.0, 12),
            ("Elephant Foot Yam (Suran) 1kg", 70.0, 45.0, "kg", 0.0, 25),
            ("Ash Gourd (Petha) 1kg", 35.0, 20.0, "kg", 0.0, 20),
            ("Red Pumpkin Cut 500g", 25.0, 14.0, "pack", 0.0, 10),
            ("Tinda (Indian Round Gourd) 500g", 40.0, 25.0, "pack", 0.0, 7),
            ("Iceberg Lettuce Crisp 1pc", 50.0, 32.0, "pcs", 0.0, 6),
            ("Romaine Lettuce Head 1pc", 60.0, 38.0, "pcs", 0.0, 6),
            ("Baby Corn Pack 200g", 45.0, 28.0, "pack", 0.0, 8),
            ("Sweet American Corn Cob 2pcs", 40.0, 24.0, "pack", 0.0, 7),
            ("Celery Bunch 250g", 55.0, 35.0, "pack", 0.0, 8),
            ("Fresh Asparagus Bunch 250g", 180.0, 125.0, "pack", 0.0, 7),
            ("Lemongrass Stalks 100g", 25.0, 14.0, "pack", 0.0, 12),
            ("Fresh Amla for Cooking 250g", 25.0, 14.0, "pack", 0.0, 14),
            ("Green Raw Mango (Kairi) 500g", 45.0, 28.0, "pack", 0.0, 10),
        ]
        catalog_raw.append(("Fresh Vegetables", "Fresh Farms Organic Produce Ltd", "VEG", veg))

        dairy = [
            ("Amul Taaza Toned Milk 1L Pouch", 54.0, 48.0, "pcs", 0.05, 3),
            ("Amul Gold Full Cream Milk 1L Pouch", 66.0, 59.0, "pcs", 0.05, 3),
            ("Amul Cow Milk 1L Pouch", 56.0, 50.0, "pcs", 0.05, 3),
            ("Amul Taaza Homogenised Toned Milk 1L Tetra", 72.0, 62.0, "pcs", 0.05, 120),
            ("Amul Gold Homogenised Milk 1L Tetra", 82.0, 71.0, "pcs", 0.05, 120),
            ("Mother Dairy Full Cream Milk 1L", 66.0, 59.0, "pcs", 0.05, 3),
            ("Mother Dairy Toned Milk 1L", 54.0, 48.0, "pcs", 0.05, 3),
            ("Mother Dairy Cow Milk 1L", 56.0, 50.0, "pcs", 0.05, 3),
            ("Raw Pressery Almond Milk Unsweetened 1L", 240.0, 190.0, "pcs", 0.05, 180),
            ("Raw Pressery Oat Milk Barista 1L", 260.0, 205.0, "pcs", 0.05, 180),
            ("Sofit Soy Milk Chocolate 1L", 145.0, 115.0, "pcs", 0.05, 180),
            ("Amul Masti Dahi Pouch 400g", 35.0, 29.0, "pcs", 0.05, 10),
            ("Amul Masti Dahi Tub 400g", 45.0, 37.0, "pcs", 0.05, 15),
            ("Mother Dairy Classic Dahi 400g", 35.0, 29.0, "pcs", 0.05, 10),
            ("Epigamia Greek Yogurt Strawberry 100g", 55.0, 42.0, "pcs", 0.05, 20),
            ("Epigamia Greek Yogurt Blueberry 100g", 55.0, 42.0, "pcs", 0.05, 20),
            ("Epigamia Greek Yogurt Natural 100g", 45.0, 34.0, "pcs", 0.05, 20),
            ("Mother Dairy Mishti Doi 85g", 20.0, 15.0, "pcs", 0.05, 12),
            ("Yakult Probiotic Drink (5x65ml Pack)", 80.0, 65.0, "pack", 0.05, 30),
            ("Amul Salted Butter 100g", 58.0, 50.0, "pcs", 0.05, 180),
            ("Amul Salted Butter 500g", 275.0, 245.0, "pcs", 0.05, 180),
            ("Amul Unsalted Cooking Butter 500g", 280.0, 248.0, "pcs", 0.05, 180),
            ("Amul Garlic & Herbs Butter 100g", 62.0, 52.0, "pcs", 0.05, 180),
            ("Nutralite Table Spread 500g", 185.0, 150.0, "pcs", 0.05, 180),
            ("Amul Malai Paneer 200g Block", 90.0, 78.0, "pcs", 0.05, 25),
            ("Amul Malai Paneer 500g Block", 215.0, 185.0, "pcs", 0.05, 25),
            ("Mother Dairy Classic Paneer 200g", 90.0, 78.0, "pcs", 0.05, 25),
            ("Go Paneer Fresh 200g", 95.0, 80.0, "pcs", 0.05, 25),
            ("Organic Tofu Soya Paneer 200g", 75.0, 55.0, "pcs", 0.05, 30),
            ("Amul Processed Cheese Slices 200g (10 slices)", 140.0, 118.0, "pack", 0.05, 180),
            ("Amul Processed Cheese Block 200g", 130.0, 108.0, "pcs", 0.05, 180),
            ("Amul Processed Cheese Cubes 200g", 135.0, 112.0, "pack", 0.05, 180),
            ("Amul Pizza Mozzarella Cheese Shredded 200g", 145.0, 120.0, "pack", 0.05, 120),
            ("Britannia Cheezza Mozzarella 200g", 150.0, 124.0, "pcs", 0.05, 120),
            ("Dlecta Cream Cheese 150g", 160.0, 125.0, "pcs", 0.05, 90),
            ("Amul Fresh Cream 250ml", 67.0, 56.0, "pcs", 0.05, 90),
            ("Amul Whipping Cream 500ml", 140.0, 115.0, "pcs", 0.05, 90),
            ("Nestle Milkmaid Sweetened Condensed Milk 380g", 144.0, 122.0, "pcs", 0.05, 240),
            ("Amul Kool Badam Drink 200ml Can", 35.0, 28.0, "pcs", 0.05, 90),
            ("Amul Kool Kesar Milk 200ml Can", 35.0, 28.0, "pcs", 0.05, 90),
            ("Amul Masala Buttermilk 200ml", 15.0, 11.0, "pcs", 0.05, 60),
            ("Mother Dairy Tadka Chach 200ml", 15.0, 11.0, "pcs", 0.05, 60),
            ("Amul Sweet Lassi 250ml Tetra", 25.0, 19.0, "pcs", 0.05, 90),
            ("Amul Mango Lassi 250ml Tetra", 28.0, 21.0, "pcs", 0.05, 90),
            ("Farm Fresh White Eggs (Pack of 6)", 48.0, 38.0, "pack", 0.05, 18),
            ("Farm Fresh White Eggs (Pack of 12)", 92.0, 74.0, "pack", 0.05, 18),
            ("Farm Fresh White Eggs (Crate of 30)", 220.0, 180.0, "pack", 0.05, 21),
            ("Eggoz Organic Brown Eggs (Pack of 6)", 75.0, 58.0, "pack", 0.05, 21),
            ("Eggoz Organic Brown Eggs (Pack of 12)", 145.0, 112.0, "pack", 0.05, 21),
            ("Eggoz Farm Omega-3 Enriched Eggs (Pack of 6)", 85.0, 65.0, "pack", 0.05, 21),
            ("Free Range Desi Country Eggs (Pack of 6)", 95.0, 72.0, "pack", 0.05, 21),
            ("Fresh Quail Eggs (Pack of 12)", 80.0, 55.0, "pack", 0.05, 21),
            ("Fresh Khoya / Mawa Pure 250g", 120.0, 95.0, "pack", 0.05, 10),
            ("Amul Shrikhand Elaichi 250g", 65.0, 52.0, "pcs", 0.05, 30),
            ("Amul Shrikhand Kesar Mango 250g", 70.0, 56.0, "pcs", 0.05, 30),
        ]
        catalog_raw.append(("Dairy & Eggs", "Amul Anand Dairy Cooperative", "DAI", dairy))

        grains = [
            ("India Gate Basmati Rice Classic 1kg", 215.0, 175.0, "pcs", 0.05, 365),
            ("India Gate Basmati Rice Classic 5kg", 990.0, 810.0, "pcs", 0.05, 365),
            ("India Gate Basmati Rice Feast Rozana 5kg", 460.0, 380.0, "pcs", 0.05, 365),
            ("Daawat Biryani Basmati Rice 1kg", 230.0, 185.0, "pcs", 0.05, 365),
            ("Daawat Biryani Basmati Rice 5kg", 1050.0, 860.0, "pcs", 0.05, 365),
            ("Daawat Super Basmati Rice 1kg", 175.0, 140.0, "pcs", 0.05, 365),
            ("Daawat Super Basmati Rice 5kg", 790.0, 640.0, "pcs", 0.05, 365),
            ("Fortune Everyday Basmati Rice 5kg", 420.0, 345.0, "pcs", 0.05, 365),
            ("Kohinoor Super Silver Basmati Rice 1kg", 165.0, 130.0, "pcs", 0.05, 365),
            ("Kohinoor Super Silver Basmati 5kg", 750.0, 610.0, "pcs", 0.05, 365),
            ("Royal Sona Masoori Rice Premium 5kg", 390.0, 320.0, "pcs", 0.05, 365),
            ("Royal Sona Masoori Rice 10kg Bag", 760.0, 620.0, "pcs", 0.05, 365),
            ("Wada Kolam Rice Superior 5kg", 430.0, 350.0, "pcs", 0.05, 365),
            ("Wada Kolam Rice 10kg Bag", 840.0, 690.0, "pcs", 0.05, 365),
            ("Organic Brown Rice Long Grain 1kg", 125.0, 95.0, "pcs", 0.05, 365),
            ("Organic Red Matta Rice 1kg", 110.0, 82.0, "pcs", 0.05, 365),
            ("Jasmine Fragrant Rice 1kg", 180.0, 140.0, "pcs", 0.05, 365),
            ("Sushi Calrose Rice 1kg", 240.0, 185.0, "pcs", 0.05, 365),
            ("Idli Short Grain Rice 1kg", 55.0, 42.0, "pcs", 0.05, 365),
            ("Govind Bhog Rice Aromatic 1kg", 140.0, 108.0, "pcs", 0.05, 365),
            ("Thick Poha Flattened Rice 500g", 38.0, 28.0, "pcs", 0.05, 180),
            ("Thin Poha Flattened Rice 500g", 40.0, 30.0, "pcs", 0.05, 180),
            ("Nylon Sabudana (Tapioca) 500g", 58.0, 44.0, "pcs", 0.05, 240),
            ("Puffed Rice (Kurmura / Murmura) 250g", 25.0, 16.0, "pcs", 0.05, 120),
            ("Aashirvaad Sharbati Whole Wheat Atta 5kg", 310.0, 260.0, "pcs", 0.05, 120),
            ("Aashirvaad Sharbati Whole Wheat Atta 10kg", 590.0, 500.0, "pcs", 0.05, 120),
            ("Aashirvaad Superior MP Chakki Atta 5kg", 270.0, 225.0, "pcs", 0.05, 120),
            ("Aashirvaad Superior MP Chakki Atta 10kg", 520.0, 440.0, "pcs", 0.05, 120),
            ("Aashirvaad Multigrain Atta 5kg", 335.0, 280.0, "pcs", 0.05, 120),
            ("Pillsbury Chakki Fresh Atta 5kg", 265.0, 220.0, "pcs", 0.05, 120),
            ("Fortune Chakki Fresh Atta 5kg", 255.0, 215.0, "pcs", 0.05, 120),
            ("Nature Fresh Sampoorna Chakki Atta 5kg", 250.0, 210.0, "pcs", 0.05, 120),
            ("Rajdhani Fine Maida 1kg", 52.0, 40.0, "pcs", 0.05, 180),
            ("Rajdhani Fine Besan (Gram Flour) 500g", 65.0, 50.0, "pcs", 0.05, 180),
            ("Rajdhani Fine Besan 1kg", 125.0, 98.0, "pcs", 0.05, 180),
            ("Tata Sampann Pure Chana Dal Besan 500g", 72.0, 56.0, "pcs", 0.05, 180),
            ("Rajdhani Sooji / Semolina 500g", 38.0, 28.0, "pcs", 0.05, 180),
            ("MTR Roasted Rava 500g", 55.0, 42.0, "pcs", 0.05, 180),
            ("Organic Ragi (Finger Millet) Flour 1kg", 85.0, 65.0, "pcs", 0.05, 180),
            ("Organic Jowar (Sorghum) Flour 1kg", 80.0, 60.0, "pcs", 0.05, 180),
            ("Organic Bajra (Pearl Millet) Flour 1kg", 75.0, 55.0, "pcs", 0.05, 180),
            ("Corn Flour Starch White 500g", 45.0, 32.0, "pcs", 0.05, 365),
            ("Fine Rice Flour 500g", 38.0, 28.0, "pcs", 0.05, 180),
            ("Bansi Rava Coarse Wheat 500g", 42.0, 32.0, "pcs", 0.05, 180),
            ("Dalia Broken Wheat 500g", 45.0, 34.0, "pcs", 0.05, 180),
            ("Organic Quinoa Grain 500g", 190.0, 145.0, "pcs", 0.05, 365),
            ("Organic Foxtail Millet 500g", 90.0, 68.0, "pcs", 0.05, 365),
            ("Organic Little Millet 500g", 95.0, 72.0, "pcs", 0.05, 365),
            ("Organic Kodo Millet 500g", 95.0, 72.0, "pcs", 0.05, 365),
            ("Organic Barnyard Millet 500g", 100.0, 75.0, "pcs", 0.05, 365),
            ("Rajdhani Rice Poha 1kg", 72.0, 54.0, "pcs", 0.05, 180),
            ("Chana Sattu Roasted Gram Flour 500g", 85.0, 65.0, "pcs", 0.05, 180),
            ("Singhade Ka Atta (Water Chestnut) 200g", 65.0, 48.0, "pcs", 0.05, 180),
            ("Kuttu Ka Atta (Buckwheat) 200g", 70.0, 52.0, "pcs", 0.05, 180),
            ("Barley (Jau) Flour 500g", 55.0, 40.0, "pcs", 0.05, 180),
            ("Organic Chia Seeds Raw 250g", 160.0, 115.0, "pcs", 0.05, 365),
            ("Organic Flax Seeds Roasted 250g", 95.0, 68.0, "pcs", 0.05, 365),
            ("Organic Pumpkin Seeds Raw 200g", 180.0, 130.0, "pcs", 0.05, 365),
            ("Organic Sunflower Seeds 200g", 130.0, 95.0, "pcs", 0.05, 365),
            ("Organic White Sesame Seeds (Til) 200g", 75.0, 54.0, "pcs", 0.05, 240),
        ]
        catalog_raw.append(("Rice & Flours", "Heritage Millers & Grains Corp", "GRA", grains))

        pulses = [
            ("Tata Sampann Unpolished Toor Dal 1kg", 185.0, 155.0, "pcs", 0.0, 365),
            ("Tata Sampann Unpolished Moong Dal 1kg", 165.0, 138.0, "pcs", 0.0, 365),
            ("Tata Sampann Moong Dal Chilka 1kg", 155.0, 128.0, "pcs", 0.0, 365),
            ("Tata Sampann Whole Green Moong 1kg", 145.0, 118.0, "pcs", 0.0, 365),
            ("Tata Sampann Chana Dal 1kg", 120.0, 98.0, "pcs", 0.0, 365),
            ("Tata Sampann Urad Dal White Split 1kg", 170.0, 142.0, "pcs", 0.0, 365),
            ("Tata Sampann Urad Whole Black 1kg", 160.0, 132.0, "pcs", 0.0, 365),
            ("Tata Sampann Masoor Dal Red Split 1kg", 115.0, 92.0, "pcs", 0.0, 365),
            ("Tata Sampann Masoor Whole Malka 1kg", 110.0, 88.0, "pcs", 0.0, 365),
            ("Tata Sampann Kabuli Chana Premium 1kg", 195.0, 160.0, "pcs", 0.0, 365),
            ("Tata Sampann Kala Chana Brown 1kg", 105.0, 84.0, "pcs", 0.0, 365),
            ("Tata Sampann Kashmiri Rajma 1kg", 210.0, 172.0, "pcs", 0.0, 365),
            ("Tata Sampann Chitra Rajma 1kg", 190.0, 155.0, "pcs", 0.0, 365),
            ("Organic White Cowpeas (Lobia) 500g", 65.0, 50.0, "pcs", 0.0, 365),
            ("Organic Red Cowpeas (Chawli) 500g", 65.0, 50.0, "pcs", 0.0, 365),
            ("Dry Green Peas (Vatana) 1kg", 110.0, 85.0, "pcs", 0.0, 365),
            ("Dry White Peas (Safed Vatana) 1kg", 95.0, 74.0, "pcs", 0.0, 365),
            ("Fortune Unpolished Arhar Toor Dal 1kg", 175.0, 145.0, "pcs", 0.0, 365),
            ("Fortune Moong Dal Dhuli 1kg", 158.0, 130.0, "pcs", 0.0, 365),
            ("Fortune Urad Dhuli Dal 1kg", 165.0, 136.0, "pcs", 0.0, 365),
            ("Fortune Chana Dal 1kg", 115.0, 92.0, "pcs", 0.0, 365),
            ("Nutrela Soya Chunks Maxi 200g", 50.0, 38.0, "pcs", 0.0, 365),
            ("Nutrela Soya Mini Chunks 200g", 50.0, 38.0, "pcs", 0.0, 365),
            ("Nutrela Soya Granules 200g", 52.0, 40.0, "pcs", 0.0, 365),
            ("Loose Premium Toor Dal 1kg", 160.0, 130.0, "kg", 0.0, 365),
            ("Loose Desi Moong Dal 1kg", 145.0, 120.0, "kg", 0.0, 365),
            ("Loose Chana Dal 1kg", 100.0, 80.0, "kg", 0.0, 365),
            ("Loose Urad Dal Gota White 1kg", 165.0, 135.0, "kg", 0.0, 365),
            ("Loose Masoor Dal 1kg", 100.0, 80.0, "kg", 0.0, 365),
            ("Loose Kabuli Big Chana 1kg", 175.0, 140.0, "kg", 0.0, 365),
            ("Loose Desi Kala Chana 1kg", 90.0, 72.0, "kg", 0.0, 365),
            ("Loose Red Kashmiri Rajma 1kg", 185.0, 150.0, "kg", 0.0, 365),
            ("Loose Brown Chitra Rajma 1kg", 165.0, 132.0, "kg", 0.0, 365),
            ("Loose Black Eyed Beans (Chawli) 1kg", 115.0, 92.0, "kg", 0.0, 365),
            ("Organic Horse Gram (Kulthi Dal) 500g", 55.0, 40.0, "pcs", 0.0, 365),
            ("Organic Moth Beans (Matki) 500g", 65.0, 48.0, "pcs", 0.0, 365),
            ("Organic Green Soyabean 500g", 70.0, 52.0, "pcs", 0.0, 365),
            ("Tata Sampann Yellow Moong Dal 500g", 85.0, 70.0, "pcs", 0.0, 365),
            ("Tata Sampann Toor Dal 500g", 95.0, 78.0, "pcs", 0.0, 365),
            ("Tata Sampann Urad Dal 500g", 88.0, 72.0, "pcs", 0.0, 365),
            ("Tata Sampann Chana Dal 500g", 62.0, 50.0, "pcs", 0.0, 365),
            ("Tata Sampann Masoor Dal 500g", 60.0, 48.0, "pcs", 0.0, 365),
            ("Organic Roasted Chana (Futana) 250g", 45.0, 32.0, "pcs", 0.0, 180),
            ("Organic Roasted Peanuts Salted 250g", 60.0, 44.0, "pcs", 0.0, 180),
            ("Raw Peanuts Groundnuts 500g", 95.0, 74.0, "pcs", 0.0, 240),
            ("Raw Peanuts Groundnuts 1kg", 180.0, 142.0, "pcs", 0.0, 240),
            ("Sprouted Mix Pulse Pack 250g", 40.0, 25.0, "pcs", 0.0, 5),
            ("Fresh Sprouted Moong 250g", 35.0, 22.0, "pcs", 0.0, 5),
            ("Fresh Sprouted Chana 250g", 35.0, 22.0, "pcs", 0.0, 5),
            ("Fresh Sprouted Matki 250g", 35.0, 22.0, "pcs", 0.0, 5),
        ]
        catalog_raw.append(("Pulses & Dals", "Heritage Millers & Grains Corp", "PUL", pulses))

        oils = [
            ("Fortune Sunlite Refined Sunflower Oil 1L Pouch", 135.0, 118.0, "pcs", 0.05, 270),
            ("Fortune Sunlite Refined Sunflower Oil 5L Can", 690.0, 595.0, "pcs", 0.05, 270),
            ("Gemini Refined Sunflower Oil 1L Pouch", 132.0, 115.0, "pcs", 0.05, 270),
            ("Gemini Refined Sunflower Oil 5L Can", 675.0, 580.0, "pcs", 0.05, 270),
            ("Saffola Gold Pro Healthy Oil 1L Pouch", 165.0, 142.0, "pcs", 0.05, 270),
            ("Saffola Gold Pro Healthy Oil 5L Can", 840.0, 720.0, "pcs", 0.05, 270),
            ("Saffola Total Heart Care Oil 1L", 195.0, 168.0, "pcs", 0.05, 270),
            ("Saffola Total Heart Care Oil 5L", 980.0, 840.0, "pcs", 0.05, 270),
            ("Fortune Kachi Ghani Pure Mustard Oil 1L Bottle", 155.0, 132.0, "pcs", 0.05, 365),
            ("Fortune Kachi Ghani Mustard Oil 5L Can", 780.0, 665.0, "pcs", 0.05, 365),
            ("Engine Brand Agmark Mustard Oil 1L", 175.0, 148.0, "pcs", 0.05, 365),
            ("Emami Healthy & Tasty Mustard Oil 1L", 150.0, 128.0, "pcs", 0.05, 365),
            ("Fortune Filtered Pure Groundnut Oil 1L", 190.0, 162.0, "pcs", 0.05, 365),
            ("Fortune Filtered Groundnut Oil 5L Can", 960.0, 815.0, "pcs", 0.05, 365),
            ("Gulab Filtered Groundnut Oil 1L", 195.0, 166.0, "pcs", 0.05, 365),
            ("Figaro Extra Virgin Olive Oil 500ml Glass", 650.0, 520.0, "pcs", 0.05, 540),
            ("Figaro Extra Virgin Olive Oil 1L Tin", 1250.0, 1020.0, "pcs", 0.05, 540),
            ("Figaro Pure Olive Cooking Oil 1L Tin", 990.0, 810.0, "pcs", 0.05, 540),
            ("Borges Extra Light Olive Oil 1L", 890.0, 720.0, "pcs", 0.05, 540),
            ("Borges Extra Virgin Olive Oil 500ml", 620.0, 495.0, "pcs", 0.05, 540),
            ("Fortune Rice Bran Health Oil 1L", 140.0, 120.0, "pcs", 0.05, 270),
            ("Fortune Rice Bran Health Oil 5L Can", 710.0, 605.0, "pcs", 0.05, 270),
            ("Parachute 100% Pure Coconut Edible Oil 500ml", 195.0, 165.0, "pcs", 0.05, 365),
            ("Parachute 100% Pure Coconut Oil 1L Tin", 380.0, 320.0, "pcs", 0.05, 365),
            ("KLF Coconad Pure Coconut Oil 1L", 360.0, 305.0, "pcs", 0.05, 365),
            ("Idhayam Pure Gingelly Sesame Oil 500ml", 220.0, 185.0, "pcs", 0.05, 365),
            ("Idhayam Pure Gingelly Sesame Oil 1L", 430.0, 360.0, "pcs", 0.05, 365),
            ("Amul Pure Desi Ghee 1L Tin", 640.0, 550.0, "pcs", 0.05, 270),
            ("Amul Pure Desi Ghee 500ml Pouch", 310.0, 268.0, "pcs", 0.05, 270),
            ("Amul Pure Desi Ghee 1L Pouch", 615.0, 530.0, "pcs", 0.05, 270),
            ("Amul Cow Ghee Pure Yellow 1L Tin", 670.0, 575.0, "pcs", 0.05, 270),
            ("Amul Cow Ghee 500ml Jar", 345.0, 295.0, "pcs", 0.05, 270),
            ("Gowardhan Pure Cow Ghee 1L Jar", 680.0, 580.0, "pcs", 0.05, 270),
            ("Gowardhan Pure Cow Ghee 500ml Jar", 350.0, 298.0, "pcs", 0.05, 270),
            ("Mother Dairy Pure Buffalo Ghee 1L", 650.0, 555.0, "pcs", 0.05, 270),
            ("Patanjali Pure Cow Ghee 1L", 620.0, 530.0, "pcs", 0.05, 270),
            ("Ananda Pure Desi Ghee 1L", 610.0, 520.0, "pcs", 0.05, 270),
            ("Dalda Vanaspati Ghee 1L Pouch", 130.0, 110.0, "pcs", 0.05, 270),
            ("Fortune Soyabean Oil 1L Pouch", 125.0, 108.0, "pcs", 0.05, 270),
            ("Fortune Soyabean Oil 5L Can", 640.0, 545.0, "pcs", 0.05, 270),
            ("Mahakosh Refined Soyabean Oil 1L", 122.0, 105.0, "pcs", 0.05, 270),
            ("Dhara Refined Mustard Oil 1L", 155.0, 132.0, "pcs", 0.05, 365),
            ("Dhara Filtered Groundnut Oil 1L", 195.0, 165.0, "pcs", 0.05, 365),
            ("Cold Pressed Virgin Coconut Oil 500ml", 320.0, 250.0, "pcs", 0.05, 365),
            ("Cold Pressed Wood Churned Groundnut Oil 1L", 280.0, 220.0, "pcs", 0.05, 365),
            ("Cold Pressed Mustard Oil 1L", 240.0, 185.0, "pcs", 0.05, 365),
            ("Cold Pressed Black Sesame Oil 500ml", 290.0, 225.0, "pcs", 0.05, 365),
            ("Cold Pressed Safflower Kardi Oil 1L", 320.0, 250.0, "pcs", 0.05, 365),
            ("Canola Healthy Cooking Oil 1L", 260.0, 205.0, "pcs", 0.05, 365),
            ("Corn Oil Mazola Heart Healthy 1L", 270.0, 215.0, "pcs", 0.05, 365),
            ("Sundrop Superlite Sunflower Oil 1L", 145.0, 124.0, "pcs", 0.05, 270),
            ("Sundrop Superlite Sunflower Oil 5L", 740.0, 630.0, "pcs", 0.05, 270),
            ("Sundrop Heart Corn Oil 1L", 230.0, 195.0, "pcs", 0.05, 270),
            ("Anik Pure Ghee 1L Tin", 630.0, 540.0, "pcs", 0.05, 270),
            ("Nestle Everyday Dairy Whitener Ghee 500ml", 330.0, 280.0, "pcs", 0.05, 270),
            ("Aashirvaad Svasti Pure Cow Ghee 1L", 695.0, 595.0, "pcs", 0.05, 270),
            ("Aashirvaad Svasti Pure Cow Ghee 500ml", 355.0, 305.0, "pcs", 0.05, 270),
            ("Milky Mist Pure Ghee 500ml", 340.0, 290.0, "pcs", 0.05, 270),
            ("Heritage Cow Ghee 1L", 660.0, 565.0, "pcs", 0.05, 270),
            ("Organic Desi A2 Gir Cow Ghee 500ml Glass", 1150.0, 890.0, "pcs", 0.05, 365),
        ]
        catalog_raw.append(("Cooking Oils & Ghee", "Metro Wholesale Agrotech", "OIL", oils))

        spices = [
            ("Tata Salt Vacuum Evaporated Iodized 1kg", 28.0, 22.0, "pcs", 0.0, 720),
            ("Tata Salt Lite Low Sodium 1kg", 45.0, 36.0, "pcs", 0.0, 720),
            ("Aashirvaad Iodized Crystal Salt 1kg", 24.0, 18.0, "pcs", 0.0, 720),
            ("Puro Pure Himalayan Pink Rock Salt 1kg", 99.0, 72.0, "pcs", 0.0, 720),
            ("Catch Black Salt (Kala Namak) Sprinkler 100g", 35.0, 25.0, "pcs", 0.0, 365),
            ("Catch Table Salt Sprinkler 100g", 30.0, 21.0, "pcs", 0.0, 365),
            ("Madhur Pure & Hygienic Sugar 1kg", 55.0, 44.0, "pcs", 0.0, 720),
            ("Madhur Pure Sugar 5kg Bag", 265.0, 215.0, "pcs", 0.0, 720),
            ("Trust Classic Pure White Sugar 1kg", 58.0, 46.0, "pcs", 0.0, 720),
            ("Organic Brown Demerara Sugar 500g", 75.0, 54.0, "pcs", 0.0, 720),
            ("Organic Sugarcane Jaggery Powder 500g", 65.0, 48.0, "pcs", 0.0, 365),
            ("Pure Kolhapur Jaggery (Gud) Cubes 1kg", 85.0, 62.0, "pcs", 0.0, 365),
            ("Everest Turmeric Powder (Haldi) 100g", 34.0, 26.0, "pcs", 0.05, 365),
            ("Everest Turmeric Powder (Haldi) 200g", 64.0, 49.0, "pcs", 0.05, 365),
            ("Everest Turmeric Powder 500g", 155.0, 120.0, "pcs", 0.05, 365),
            ("Everest Tikhalal Red Chilli Powder 100g", 48.0, 37.0, "pcs", 0.05, 365),
            ("Everest Tikhalal Red Chilli Powder 200g", 94.0, 73.0, "pcs", 0.05, 365),
            ("Everest Tikhalal Chilli Powder 500g", 230.0, 180.0, "pcs", 0.05, 365),
            ("Everest Kashmirilal Mild Red Chilli 100g", 78.0, 60.0, "pcs", 0.05, 365),
            ("Everest Coriander Powder (Dhania) 100g", 36.0, 27.0, "pcs", 0.05, 365),
            ("Everest Coriander Powder 200g", 68.0, 52.0, "pcs", 0.05, 365),
            ("Everest Garam Masala Royal 100g", 88.0, 68.0, "pcs", 0.05, 365),
            ("Everest Kitchen King Masala 100g", 78.0, 60.0, "pcs", 0.05, 365),
            ("Everest Pav Bhaji Masala 100g", 75.0, 58.0, "pcs", 0.05, 365),
            ("Everest Chhole Masala 100g", 76.0, 58.0, "pcs", 0.05, 365),
            ("Everest Sambhar Masala 100g", 72.0, 55.0, "pcs", 0.05, 365),
            ("Everest Shahi Paneer Masala 100g", 82.0, 63.0, "pcs", 0.05, 365),
            ("Everest Biryani Masala 100g", 85.0, 65.0, "pcs", 0.05, 365),
            ("Everest Chaat Masala 100g", 68.0, 52.0, "pcs", 0.05, 365),
            ("MDH Deggi Mirch Powder 100g", 85.0, 66.0, "pcs", 0.05, 365),
            ("MDH Chunky Chat Masala 100g", 72.0, 55.0, "pcs", 0.05, 365),
            ("MDH Kasoori Methi Dry Leaves 100g", 65.0, 50.0, "pcs", 0.05, 365),
            ("MDH Chana Masala 100g", 78.0, 60.0, "pcs", 0.05, 365),
            ("MDH Dal Makhani Masala 100g", 80.0, 62.0, "pcs", 0.05, 365),
            ("Catch Compounded Asafoetida Hing 50g", 75.0, 56.0, "pcs", 0.05, 365),
            ("LG Compound Asafoetida Powder 50g", 80.0, 62.0, "pcs", 0.05, 365),
            ("Tata Sampann Cumin Seeds (Jeera) 100g", 82.0, 64.0, "pcs", 0.05, 365),
            ("Tata Sampann Mustard Seeds (Rai) 100g", 32.0, 24.0, "pcs", 0.05, 365),
            ("Tata Sampann Fennel Seeds (Saunf) 100g", 45.0, 34.0, "pcs", 0.05, 365),
            ("Tata Sampann Fenugreek (Methi) Seeds 100g", 30.0, 22.0, "pcs", 0.05, 365),
            ("Tata Sampann Ajwain Carom Seeds 100g", 42.0, 32.0, "pcs", 0.05, 365),
            ("Tata Sampann Black Pepper Whole (Kali Mirch) 100g", 125.0, 95.0, "pcs", 0.05, 365),
            ("Tata Sampann Cloves (Laung) 50g", 85.0, 65.0, "pcs", 0.05, 365),
            ("Tata Sampann Green Cardamom (Elaichi) 50g", 195.0, 150.0, "pcs", 0.05, 365),
            ("Tata Sampann Cinnamon Sticks (Dalchini) 50g", 55.0, 40.0, "pcs", 0.05, 365),
            ("Tata Sampann Bay Leaves (Tejpatta) 50g", 35.0, 24.0, "pcs", 0.05, 365),
            ("Whole Star Anise (Chakra Phool) 50g", 70.0, 50.0, "pcs", 0.05, 365),
            ("Whole Black Cardamom (Badi Elaichi) 50g", 110.0, 82.0, "pcs", 0.05, 365),
            ("Whole Nutmeg (Jaiphal) Pack 4pcs", 65.0, 48.0, "pcs", 0.05, 365),
            ("Mace Flower (Javitri) 25g", 85.0, 62.0, "pcs", 0.05, 365),
            ("Amchur (Dry Mango) Powder 100g", 55.0, 40.0, "pcs", 0.05, 365),
            ("Dry Ginger Powder (Saunth) 100g", 65.0, 48.0, "pcs", 0.05, 365),
            ("White Sesame Seeds Natural 100g", 40.0, 28.0, "pcs", 0.05, 240),
            ("Black Sesame Seeds Natural 100g", 48.0, 34.0, "pcs", 0.05, 240),
            ("Dry Curry Leaves Flakes 25g", 30.0, 20.0, "pcs", 0.05, 240),
            ("Biryani Whole Khada Masala Potli 50g", 65.0, 46.0, "pcs", 0.05, 365),
            ("Pani Puri Masala Powder 100g", 45.0, 32.0, "pcs", 0.05, 365),
            ("Jaljeera Masala Powder 100g", 42.0, 30.0, "pcs", 0.05, 365),
            ("Pasta & Pizza Oregano Herb Seasoning 50g", 75.0, 52.0, "pcs", 0.05, 365),
            ("Chilli Flakes Sprinkler 50g", 75.0, 52.0, "pcs", 0.05, 365),
        ]
        catalog_raw.append(("Spices & Seasonings", "Metro Wholesale Agrotech", "SPI", spices))

        beverages = [
            ("Tata Tea Gold Premium 500g", 325.0, 275.0, "pcs", 0.12, 365),
            ("Tata Tea Gold Premium 1kg", 620.0, 525.0, "pcs", 0.12, 365),
            ("Tata Tea Premium Desh Ki Chai 500g", 270.0, 225.0, "pcs", 0.12, 365),
            ("Tata Tea Premium 1kg", 510.0, 430.0, "pcs", 0.12, 365),
            ("Tata Tea Agni Strong 500g", 180.0, 150.0, "pcs", 0.12, 365),
            ("Brooke Bond Red Label Tea 500g", 285.0, 240.0, "pcs", 0.12, 365),
            ("Brooke Bond Red Label Tea 1kg", 540.0, 455.0, "pcs", 0.12, 365),
            ("Brooke Bond Red Label Natural Care 500g", 340.0, 285.0, "pcs", 0.12, 365),
            ("Brooke Bond Taj Mahal Rich CTC Tea 500g", 390.0, 325.0, "pcs", 0.12, 365),
            ("Wagh Bakri Premium Leaf Tea 500g", 310.0, 260.0, "pcs", 0.12, 365),
            ("Wagh Bakri Spiced Masala Tea 250g", 185.0, 150.0, "pcs", 0.12, 365),
            ("Twinings Green Tea Pure (25 Tea Bags)", 220.0, 175.0, "pack", 0.12, 540),
            ("Twinings Earl Grey Tea (25 Tea Bags)", 290.0, 230.0, "pack", 0.12, 540),
            ("Twinings English Breakfast (25 Tea Bags)", 290.0, 230.0, "pack", 0.12, 540),
            ("Lipton Pure & Light Green Tea (25 Bags)", 165.0, 130.0, "pack", 0.12, 540),
            ("Lipton Honey Lemon Green Tea (25 Bags)", 185.0, 145.0, "pack", 0.12, 540),
            ("Tetley Ginger Mint Lemon Green Tea (25 Bags)", 180.0, 140.0, "pack", 0.12, 540),
            ("Organic India Tulsi Green Tea Classic (25 Bags)", 195.0, 155.0, "pack", 0.12, 540),
            ("Organic India Tulsi Mulethi Infusion (25 Bags)", 210.0, 165.0, "pack", 0.12, 540),
            ("Nescafe Classic Pure Instant Coffee 100g Jar", 340.0, 280.0, "pcs", 0.12, 540),
            ("Nescafe Classic Pure Instant Coffee 200g Jar", 640.0, 530.0, "pcs", 0.12, 540),
            ("Nescafe Sunrise Chicory Blend Coffee 200g", 380.0, 310.0, "pcs", 0.12, 540),
            ("Bru Instant Coffee Pure Chicory Blend 100g", 240.0, 195.0, "pcs", 0.12, 540),
            ("Bru Instant Coffee 200g Jar", 460.0, 375.0, "pcs", 0.12, 540),
            ("Bru Gold 100% Pure Granulated Coffee 100g", 350.0, 285.0, "pcs", 0.12, 540),
            ("Davidoff Rich Aroma Fine Coffee 100g", 690.0, 550.0, "pcs", 0.12, 540),
            ("Blue Tokai Attikan Estate Ground Coffee 250g", 490.0, 390.0, "pcs", 0.12, 180),
            ("Blue Tokai Roasted Arabica Beans 250g", 490.0, 390.0, "pcs", 0.12, 180),
            ("Narasu's Ananda Filter Coffee 500g", 280.0, 230.0, "pcs", 0.12, 180),
            ("Real Fruit Power Mixed Fruit Juice 1L", 130.0, 105.0, "pcs", 0.12, 210),
            ("Real Fruit Power Alphonso Mango Juice 1L", 130.0, 105.0, "pcs", 0.12, 210),
            ("Real Fruit Power Himalayan Apple Juice 1L", 130.0, 105.0, "pcs", 0.12, 210),
            ("Real Fruit Power Mosambi Sweet Lime 1L", 130.0, 105.0, "pcs", 0.12, 210),
            ("Tropicana 100% Orange Juice 1L", 155.0, 125.0, "pcs", 0.12, 210),
            ("Tropicana 100% Apple Delight Juice 1L", 155.0, 125.0, "pcs", 0.12, 210),
            ("B Natural Guava Gush Juice 1L", 120.0, 96.0, "pcs", 0.12, 210),
            ("B Natural Pomegranate Juice 1L", 140.0, 112.0, "pcs", 0.12, 210),
            ("Raw Pressery Valencia Orange 100% Cold Juice 200ml", 90.0, 70.0, "pcs", 0.12, 30),
            ("Raw Pressery Pure Coconut Water 200ml", 60.0, 45.0, "pcs", 0.12, 60),
            ("Paper Boat Aamras Alphonso Mango 250ml", 35.0, 26.0, "pcs", 0.12, 120),
            ("Paper Boat Jaljeera Classic 250ml", 35.0, 26.0, "pcs", 0.12, 120),
            ("Paper Boat Chilli Guava 250ml", 35.0, 26.0, "pcs", 0.12, 120),
            ("Coca-Cola Original Taste 750ml Bottle", 45.0, 35.0, "pcs", 0.12, 180),
            ("Coca-Cola Zero Sugar Can 300ml", 40.0, 30.0, "pcs", 0.12, 180),
            ("Thums Up Strong Taste 750ml Bottle", 45.0, 35.0, "pcs", 0.12, 180),
            ("Sprite Clear Lime 750ml Bottle", 45.0, 35.0, "pcs", 0.12, 180),
            ("Schweppes Tonic Water Can 300ml", 60.0, 45.0, "pcs", 0.12, 240),
            ("Schweppes Ginger Ale Can 300ml", 60.0, 45.0, "pcs", 0.12, 240),
            ("Red Bull Energy Drink Can 250ml", 125.0, 98.0, "pcs", 0.12, 365),
            ("Kinley Club Soda 750ml Bottle", 20.0, 14.0, "pcs", 0.12, 180),
            ("Bisleri Mineral Water 1L Bottle", 20.0, 13.0, "pcs", 0.12, 180),
            ("Bisleri Mineral Water 5L Can", 75.0, 52.0, "pcs", 0.12, 180),
            ("Bournvita Chocolate Health Nutrition 500g Jar", 265.0, 220.0, "pcs", 0.12, 365),
            ("Horlicks Classic Malt Health Drink 500g Jar", 275.0, 228.0, "pcs", 0.12, 365),
            ("Cadbury Hot Chocolate Drink Mix 200g", 160.0, 128.0, "pcs", 0.12, 365),
        ]
        catalog_raw.append(("Beverages & Tea", "Hindustan FMCG Mega Distributors", "BEV", beverages))

        snacks = [
            ("Britannia Good Day Cashew Cookies 200g", 45.0, 36.0, "pcs", 0.18, 180),
            ("Britannia Good Day Butter Cookies 200g", 40.0, 32.0, "pcs", 0.18, 180),
            ("Britannia Marie Gold Crisp Biscuits 300g", 42.0, 33.0, "pcs", 0.18, 180),
            ("Britannia NutriChoice Digestive Biscuits 250g", 65.0, 52.0, "pcs", 0.18, 180),
            ("Britannia Bourbon Chocolate Cream 150g", 35.0, 27.0, "pcs", 0.18, 180),
            ("Britannia Little Hearts Sugar Glazed 75g", 25.0, 19.0, "pcs", 0.18, 180),
            ("Parle-G Gold Original Glucose Biscuits 250g", 30.0, 24.0, "pcs", 0.18, 180),
            ("Parle Monaco Salted Crackers 200g", 35.0, 27.0, "pcs", 0.18, 180),
            ("Parle Krackjack Sweet & Salty 200g", 35.0, 27.0, "pcs", 0.18, 180),
            ("Parle Hide & Seek Chocolate Chip 120g", 40.0, 31.0, "pcs", 0.18, 180),
            ("Sunfeast Dark Fantasy Choco Fills 300g", 130.0, 102.0, "pcs", 0.18, 180),
            ("Sunfeast Mom's Magic Cashew Almond 200g", 45.0, 35.0, "pcs", 0.18, 180),
            ("Oreo Original Vanilla Creme Cookies 120g", 40.0, 31.0, "pcs", 0.18, 180),
            ("Oreo Strawberry Creme Cookies 120g", 40.0, 31.0, "pcs", 0.18, 180),
            ("Lay's India's Magic Masala Chips 50g", 20.0, 15.0, "pcs", 0.18, 120),
            ("Lay's Classic Salted Potato Chips 50g", 20.0, 15.0, "pcs", 0.18, 120),
            ("Lay's American Style Cream & Onion 50g", 20.0, 15.0, "pcs", 0.18, 120),
            ("Lay's Spanish Tomato Tango 50g", 20.0, 15.0, "pcs", 0.18, 120),
            ("Kurkure Masala Munch Crunchy 85g", 20.0, 15.0, "pcs", 0.18, 120),
            ("Kurkure Green Chutney Style 85g", 20.0, 15.0, "pcs", 0.18, 120),
            ("Doritos Nacho Cheese Tortilla Chips 140g", 90.0, 70.0, "pcs", 0.18, 180),
            ("Doritos Sweet Chilli Tortilla Chips 140g", 90.0, 70.0, "pcs", 0.18, 180),
            ("Haldiram's Nagpur Aloo Bhujia 400g", 115.0, 92.0, "pcs", 0.18, 180),
            ("Haldiram's Bhujia Sev 400g", 115.0, 92.0, "pcs", 0.18, 180),
            ("Haldiram's Khatta Meetha Mixture 400g", 110.0, 88.0, "pcs", 0.18, 180),
            ("Haldiram's Moong Dal Fried Namkeen 200g", 65.0, 52.0, "pcs", 0.18, 180),
            ("Haldiram's Salted Roasted Cashews 200g", 280.0, 225.0, "pcs", 0.18, 180),
            ("Haldiram's Salted Roasted Almonds 200g", 250.0, 198.0, "pcs", 0.18, 180),
            ("Haldiram's Salted Roasted Pistachios 200g", 310.0, 245.0, "pcs", 0.18, 180),
            ("Kerala Style Salted Banana Chips 200g", 90.0, 68.0, "pcs", 0.18, 90),
            ("Cadbury Dairy Milk Chocolate Bar 50g", 45.0, 36.0, "pcs", 0.18, 365),
            ("Cadbury Dairy Milk Silk Chocolate 150g", 175.0, 140.0, "pcs", 0.18, 365),
            ("Cadbury Dairy Milk Fruit & Nut 80g", 95.0, 76.0, "pcs", 0.18, 365),
            ("Cadbury Dairy Milk Roast Almond 80g", 95.0, 76.0, "pcs", 0.18, 365),
            ("Amul Dark Chocolate 70% Intense 150g", 120.0, 95.0, "pcs", 0.18, 365),
            ("Amul 55% Rich Dark Chocolate 150g", 110.0, 88.0, "pcs", 0.18, 365),
            ("Amul Fruit & Nut Dark Chocolate 150g", 130.0, 102.0, "pcs", 0.18, 365),
            ("Ferrero Rocher Chocolate Box (Pack of 16)", 595.0, 480.0, "pack", 0.18, 270),
            ("Nutella Hazelnut Cocoa Spread 350g", 390.0, 315.0, "pcs", 0.18, 365),
            ("Nestle Maggi 2-Minute Masala Noodles 280g (4-Pack)", 58.0, 47.0, "pack", 0.18, 270),
            ("Nestle Maggi 2-Minute Special Masala 70g", 18.0, 14.0, "pcs", 0.18, 270),
            ("Nestle Maggi Atta Masala Noodles 290g", 95.0, 76.0, "pack", 0.18, 270),
            ("Top Ramen Curry Noodles 280g (4-Pack)", 52.0, 41.0, "pack", 0.18, 270),
            ("Ching's Secret Schezwan Noodles 240g", 55.0, 43.0, "pack", 0.18, 270),
            ("Nongshim Shin Ramyun Spicy Noodles 120g", 130.0, 100.0, "pcs", 0.18, 365),
            ("Borges Penne Rigate Durum Wheat Pasta 500g", 145.0, 110.0, "pcs", 0.18, 720),
            ("Borges Spaghetti Italian Pasta 500g", 145.0, 110.0, "pcs", 0.18, 720),
            ("Borges Fusilli Spiral Pasta 500g", 145.0, 110.0, "pcs", 0.18, 720),
            ("Bambino Macaroni Pasta 500g", 65.0, 48.0, "pcs", 0.18, 365),
            ("Bambino Roasted Vermicelli 450g", 55.0, 40.0, "pcs", 0.18, 365),
            ("Barilla Traditional Basilico Pasta Sauce 400g", 290.0, 225.0, "pcs", 0.18, 540),
            ("Veeba Pizza & Pasta Sauce 350g", 99.0, 76.0, "pcs", 0.18, 270),
            ("Kissan Fresh Tomato Ketchup 950g Squeezo", 145.0, 115.0, "pcs", 0.18, 270),
            ("Maggi Rich Tomato Ketchup 1kg Bottle", 155.0, 122.0, "pcs", 0.18, 270),
            ("Veeba Eggless Mayonnaise Original 250g", 85.0, 66.0, "pcs", 0.18, 180),
            ("Ching's Secret Schezwan Chutney 250g", 85.0, 66.0, "pcs", 0.18, 270),
            ("FunFoods Peanut Butter Creamy 350g", 165.0, 128.0, "pcs", 0.18, 365),
            ("FunFoods Peanut Butter Crunchy 350g", 165.0, 128.0, "pcs", 0.18, 365),
            ("Kissan Mixed Fruit Jam 500g Jar", 175.0, 138.0, "pcs", 0.18, 365),
            ("Haldiram's Gulab Jamun Tin 1kg", 240.0, 190.0, "pcs", 0.18, 365),
            ("Haldiram's Rasgulla Sweet Tin 1kg", 230.0, 182.0, "pcs", 0.18, 365),
            ("Haldiram's Kaju Katli Gift Box 250g", 320.0, 255.0, "pcs", 0.18, 60),
            ("Haldiram's Soan Papdi Elaichi 400g", 140.0, 110.0, "pcs", 0.18, 180),
            ("Chupa Chups Sour Bites Candy 55g", 35.0, 26.0, "pcs", 0.18, 365),
            ("Mentos Mint Roll Chewy Candy 37g", 15.0, 10.0, "pcs", 0.18, 365),
        ]
        catalog_raw.append(("Snacks & Biscuits", "Hindustan FMCG Mega Distributors", "SNK", snacks))

        cleaning = [
            ("Vim Lemon Dishwash Liquid Gel 750ml", 170.0, 135.0, "pcs", 0.18, 720),
            ("Vim Lemon Dishwash Gel 500ml", 120.0, 95.0, "pcs", 0.18, 720),
            ("Vim Dishwash Bar with Polycoat 300g", 30.0, 23.0, "pcs", 0.18, 720),
            ("Pril Lime Dishwashing Liquid 425ml", 110.0, 85.0, "pcs", 0.18, 720),
            ("Scotch-Brite Heavy Duty Scrub Sponge (Pack of 3)", 95.0, 72.0, "pack", 0.18, 1080),
            ("Scotch-Brite Stainless Steel Scrubber (Pack of 2)", 60.0, 44.0, "pack", 0.18, 1080),
            ("Surf Excel Easy Wash Detergent Powder 1kg", 145.0, 118.0, "pcs", 0.18, 720),
            ("Surf Excel Matic Front Load Powder 2kg", 460.0, 380.0, "pcs", 0.18, 720),
            ("Surf Excel Matic Top Load Liquid 1L", 220.0, 178.0, "pcs", 0.18, 720),
            ("Ariel Matic Front Load Detergent 2kg", 480.0, 395.0, "pcs", 0.18, 720),
            ("Ariel Complete Detergent Powder 1kg", 155.0, 126.0, "pcs", 0.18, 720),
            ("Tide Plus Extra Power Jasmine Detergent 1kg", 125.0, 100.0, "pcs", 0.18, 720),
            ("Rin Detergent Bar 250g (Pack of 4)", 85.0, 68.0, "pack", 0.18, 720),
            ("Comfort Morning Fresh Fabric Conditioner 860ml", 225.0, 180.0, "pcs", 0.18, 720),
            ("Lizol Citrus Disinfectant Floor Cleaner 1L", 215.0, 172.0, "pcs", 0.18, 720),
            ("Lizol Lavender Floral Floor Cleaner 2L", 390.0, 310.0, "pcs", 0.18, 720),
            ("Harpic Power Plus Disinfectant Toilet Cleaner 1L", 210.0, 168.0, "pcs", 0.18, 720),
            ("Harpic Bathroom Cleaner Lemon 500ml", 105.0, 82.0, "pcs", 0.18, 720),
            ("Colin Glass & Surface Cleaner Spray 500ml", 105.0, 82.0, "pcs", 0.18, 720),
            ("Dettol Antiseptic Liquid Disinfectant 550ml", 215.0, 175.0, "pcs", 0.18, 720),
            ("Savlon Antiseptic Liquid 500ml", 160.0, 128.0, "pcs", 0.18, 720),
            ("Godrej aer Pocket Bathroom Fragrance 10g", 65.0, 48.0, "pcs", 0.18, 365),
            ("Odonil Bathroom Air Freshener Blocks 50g x 4", 175.0, 135.0, "pack", 0.18, 365),
            ("All Out Ultra Mosquito Repellent Refill (Twin Pack)", 155.0, 120.0, "pack", 0.18, 720),
            ("Good Knight Gold Flash Liquid Vaporizer 45ml", 85.0, 66.0, "pcs", 0.18, 720),
            ("Hit Flying Insect Killer Spray 400ml", 210.0, 165.0, "pcs", 0.18, 720),
            ("Hit Crawling Cockroach Killer Spray 400ml", 220.0, 172.0, "pcs", 0.18, 720),
            ("Origami Kitchen Paper Towel 2 Ply (Pack of 2 Rolls)", 135.0, 102.0, "pack", 0.18, 1080),
            ("Paseo Ultra Soft Toilet Tissue Rolls (Pack of 4)", 160.0, 120.0, "pack", 0.18, 1080),
            ("Freshwrapp Food Grade Aluminum Foil 18m", 155.0, 118.0, "pcs", 0.18, 1080),
            ("Freshwrapp Food Grade Aluminum Foil 72m", 480.0, 380.0, "pcs", 0.18, 1080),
            ("Asahi Kasei Cling Wrap Film 30m", 175.0, 130.0, "pcs", 0.18, 1080),
            ("Shalimar Garbage Dustbin Bags Medium (Pack of 30)", 95.0, 70.0, "pack", 0.18, 1080),
            ("Shalimar Garbage Dustbin Bags Large (Pack of 30)", 135.0, 98.0, "pack", 0.18, 1080),
            ("Gala Dustpan with Hand Wiper Set", 190.0, 140.0, "pcs", 0.18, 1080),
            ("Gala Spin Mop Quick Wet Floor Cleaner", 899.0, 680.0, "pcs", 0.18, 1080),
            ("Gala Floor Wiper Squeegee 40cm", 180.0, 130.0, "pcs", 0.18, 1080),
            ("Gala Microfiber Floor Duster Cloth", 120.0, 85.0, "pcs", 0.18, 1080),
            ("Camphor Pure Aarti Pooja Tablets 100g", 120.0, 85.0, "pcs", 0.18, 720),
            ("Cycle Pure Agarbatti Incense Sticks (Pack of 3)", 150.0, 110.0, "pack", 0.18, 720),
            ("Mangaldeep Sandalwood Agarbatti 100 Sticks", 80.0, 58.0, "pcs", 0.18, 720),
            ("Duracell Ultra AA Alkaline Batteries (Pack of 4)", 180.0, 135.0, "pack", 0.18, 1800),
            ("Duracell Ultra AAA Alkaline Batteries (Pack of 4)", 180.0, 135.0, "pack", 0.18, 1800),
            ("Eveready Heavy Duty 9V Battery 1pc", 55.0, 40.0, "pcs", 0.18, 1080),
            ("Philips 9W Cool Day White LED Bulb 1pc", 110.0, 80.0, "pcs", 0.18, 1080),
            ("Fevikwik Instant Adhesive Glue 3g", 10.0, 7.0, "pcs", 0.18, 365),
            ("Fevicol MR Squeeze Bottle Glue 100g", 45.0, 32.0, "pcs", 0.18, 720),
            ("Safety Matches Box Premium (Bundle of 10)", 30.0, 20.0, "pack", 0.18, 1080),
            ("Candles White Dinner Pack (Pack of 6)", 60.0, 42.0, "pack", 0.18, 1800),
            ("Cotton Balls Sterile White 100g", 65.0, 45.0, "pcs", 0.18, 1080),
            ("Baking Soda Pure Food Grade 100g", 30.0, 20.0, "pcs", 0.18, 720),
            ("Eno Fruit Salt Regular Lemon 100g Bottle", 175.0, 138.0, "pcs", 0.18, 720),
            ("Disinfectant Surface Spray Air Sanitizer 240ml", 199.0, 150.0, "pcs", 0.18, 720),
            ("Multi-purpose Kitchen Microfiber Duster 3pcs", 150.0, 105.0, "pack", 0.18, 1080),
            ("Napthalene White Balls for Cupboards 200g", 55.0, 38.0, "pack", 0.18, 1080),
        ]
        catalog_raw.append(("Cleaning & Household", "Hindustan FMCG Mega Distributors", "HOU", cleaning))

        bakery = [
            ("Britannia 100% Whole Wheat Brown Bread 400g", 45.0, 34.0, "pcs", 0.05, 5),
            ("Britannia White Sandwich Bread 400g", 38.0, 28.0, "pcs", 0.05, 5),
            ("Britannia Multigrain Fiber Bread 400g", 55.0, 42.0, "pcs", 0.05, 5),
            ("English Oven Artisan Sourdough Loaf 400g", 90.0, 68.0, "pcs", 0.05, 4),
            ("English Oven Garlic Bread Loaf 250g", 65.0, 48.0, "pcs", 0.05, 4),
            ("English Oven Pav Buns (Pack of 6)", 35.0, 24.0, "pack", 0.05, 4),
            ("English Oven Burger Buns Sesame (Pack of 4)", 45.0, 32.0, "pack", 0.05, 5),
            ("English Oven Hot Dog Rolls (Pack of 4)", 45.0, 32.0, "pack", 0.05, 5),
            ("Modern Soft White Bread 400g", 35.0, 26.0, "pcs", 0.05, 5),
            ("Modern 100% Whole Wheat Bread 400g", 42.0, 32.0, "pcs", 0.05, 5),
            ("Britannia Toastea Premium Wheat Rusk 400g", 60.0, 46.0, "pcs", 0.05, 180),
            ("Britannia Toastea Milk Rusk 400g", 55.0, 42.0, "pcs", 0.05, 180),
            ("Britannia Fruit Cake Slice 120g", 30.0, 22.0, "pcs", 0.05, 90),
            ("Britannia Chocolate Cake Bar 120g", 30.0, 22.0, "pcs", 0.05, 90),
            ("Kellogg's Corn Flakes Original 500g", 195.0, 155.0, "pcs", 0.05, 365),
            ("Kellogg's Corn Flakes Real Almond Honey 300g", 185.0, 145.0, "pcs", 0.05, 365),
            ("Kellogg's Chocos Fills Chocolate Cereal 250g", 140.0, 108.0, "pcs", 0.05, 270),
            ("Quaker Rolled Whole Oats 1kg", 199.0, 158.0, "pcs", 0.05, 365),
            ("Saffola Masala Oats Classic Masala 500g", 175.0, 138.0, "pcs", 0.05, 270),
            ("Saffola Masala Oats Veggie Twist 500g", 175.0, 138.0, "pcs", 0.05, 270),
            ("Kellogg's Muesli Fruit Nut & Seeds 400g", 295.0, 235.0, "pcs", 0.05, 270),
            ("Bagrry's Crunchy Muesli 400g", 280.0, 220.0, "pcs", 0.05, 270),
            ("Yogabar Dark Chocolate Granola 350g", 275.0, 215.0, "pcs", 0.05, 180),
            ("Betty Crocker Buttermilk Pancake Mix 400g", 145.0, 110.0, "pcs", 0.05, 365),
            ("Hershey's Chocolate Syrup Bottle 650g", 230.0, 180.0, "pcs", 0.05, 365),
        ]
        catalog_raw.append(("Bakery & Breads", "Hindustan FMCG Mega Distributors", "BAK", bakery))

        personal_care = [
            ("Dettol Original Bathing Soap Bar 125g (Pack of 4)", 185.0, 145.0, "pack", 0.18, 720),
            ("Dettol Skincare Soap Bar 125g (Pack of 4)", 195.0, 152.0, "pack", 0.18, 720),
            ("Dove Cream Beauty Bathing Bar 100g (Pack of 3)", 210.0, 165.0, "pack", 0.18, 720),
            ("Pears Pure & Gentle Glycerin Soap 125g (Pack of 3)", 240.0, 188.0, "pack", 0.18, 720),
            ("Lifebuoy Total Germ Protection Soap 125g (Pack of 4)", 140.0, 108.0, "pack", 0.18, 720),
            ("Fiama Gel Bar Peach & Avocado 125g (Pack of 3)", 225.0, 175.0, "pack", 0.18, 720),
            ("Nivea Deep Impact Men Shower Gel 250ml", 199.0, 150.0, "pcs", 0.18, 720),
            ("Dettol Original Germ Protection Liquid Handwash 750ml Refill", 119.0, 88.0, "pcs", 0.18, 720),
            ("Lifebuoy Total 10 Handwash 750ml Refill", 109.0, 82.0, "pcs", 0.18, 720),
            ("Colgate Total Dental Cavity Protection Toothpaste 150g", 140.0, 108.0, "pcs", 0.18, 720),
            ("Colgate MaxFresh Spicy Red Gel Toothpaste 150g", 125.0, 96.0, "pcs", 0.18, 720),
            ("Sensodyne Fresh Gel Sensitive Teeth Toothpaste 150g", 240.0, 188.0, "pcs", 0.18, 720),
            ("Dabur Red Ayurvedic Toothpaste 200g", 130.0, 100.0, "pcs", 0.18, 720),
            ("Oral-B Shiny Clean Soft Toothbrush (Pack of 4)", 85.0, 60.0, "pack", 0.18, 1080),
            ("Colgate ZigZag Charcoal Toothbrush (Pack of 4)", 99.0, 72.0, "pack", 0.18, 1080),
            ("Listerine Cool Mint Mouthwash 250ml", 160.0, 124.0, "pcs", 0.18, 720),
            ("Head & Shoulders Cool Menthol Anti-Dandruff Shampoo 340ml", 360.0, 285.0, "pcs", 0.18, 720),
            ("Head & Shoulders Smooth & Silky Shampoo 340ml", 360.0, 285.0, "pcs", 0.18, 720),
            ("Dove Intense Repair Shampoo 340ml", 340.0, 268.0, "pcs", 0.18, 720),
            ("Dove Intense Repair Hair Conditioner 175ml", 220.0, 172.0, "pcs", 0.18, 720),
            ("Pantene Pro-V Hair Fall Control Shampoo 340ml", 340.0, 268.0, "pcs", 0.18, 720),
            ("Parachute Advansed Aloe Vera Coconut Hair Oil 250ml", 160.0, 125.0, "pcs", 0.18, 720),
            ("Bajaj Almond Drops Non-Sticky Hair Oil 200ml", 155.0, 120.0, "pcs", 0.18, 720),
            ("Dabur Amla Hair Oil 275ml", 140.0, 108.0, "pcs", 0.18, 720),
            ("Gillette Fusion 5 Proglide Razor Handle with Cartridge", 499.0, 390.0, "pcs", 0.18, 1080),
            ("Gillette Mach 3 Shaving Blades (Pack of 4 Cartridges)", 550.0, 440.0, "pack", 0.18, 1080),
            ("Gillette Classic Sensitive Shaving Foam 418g", 245.0, 190.0, "pcs", 0.18, 720),
            ("Old Spice Original After Shave Lotion 100ml", 260.0, 205.0, "pcs", 0.18, 720),
            ("Nivea Men Fresh Active Deodorant Spray 150ml", 225.0, 175.0, "pcs", 0.18, 720),
            ("Fogg Impressio Fragrance Body Spray 150ml", 270.0, 210.0, "pcs", 0.18, 720),
            ("Vaseline Deep Moisture Body Lotion 400ml", 340.0, 265.0, "pcs", 0.18, 720),
            ("Nivea Soft Light Moisturizing Cream 200ml", 299.0, 230.0, "pcs", 0.18, 720),
            ("Himalaya Purifying Neem Face Wash 150ml", 195.0, 150.0, "pcs", 0.18, 720),
            ("Garnier Men Acno Fight Anti-Pimple Face Wash 100g", 199.0, 152.0, "pcs", 0.18, 720),
            ("Whisper Ultra Clean Sanitary Pads XL+ (Pack of 30)", 360.0, 280.0, "pack", 0.18, 1080),
            ("Stayfree Secure Cottony Soft Sanitary Pads (Pack of 28)", 175.0, 135.0, "pack", 0.18, 1080),
            ("Pampers All Round Protection Baby Diaper Pants L (34 count)", 599.0, 470.0, "pack", 0.18, 720),
            ("Huggies Wonder Pants Baby Diapers M (42 count)", 649.0, 510.0, "pack", 0.18, 720),
            ("Johnson's Baby Gentle No Tears Shampoo 200ml", 195.0, 150.0, "pcs", 0.18, 720),
            ("Johnson's Baby Soft Moisturizing Lotion 200ml", 195.0, 150.0, "pcs", 0.18, 720),
        ]
        catalog_raw.append(("Personal Care", "Hindustan FMCG Mega Distributors", "CAR", personal_care))

        # Build final Product instances
        products_to_add = []
        barcode_counter = 890100000001
        today = date.today()

        for cat_name, supp_name, sku_prefix, items_list in catalog_raw:
            category_obj = seeded_categories.get(cat_name)
            supplier_obj = seeded_suppliers.get(supp_name)

            for idx, item in enumerate(items_list):
                name, price, cost, unit, tax_rate, shelf_days = item
                barcode_str = str(barcode_counter)
                barcode_counter += 1

                if barcode_str in existing_barcodes:
                    continue

                sku_str = f"{sku_prefix}-{idx+1:03d}"
                exp_date = today + timedelta(days=shelf_days)
                stock_amt = round(random.uniform(25.0, 180.0), 1 if unit in ['kg', 'L'] else 0)

                product_obj = Product(
                    barcode=barcode_str,
                    sku=sku_str,
                    name=name,
                    description=f"{name} - Fresh retail grocery supply.",
                    category_id=category_obj.id,
                    supplier_id=supplier_obj.id if supplier_obj else None,
                    price=price,
                    cost_price=cost,
                    stock_quantity=stock_amt,
                    min_stock_alert=15.0,
                    unit=unit,
                    tax_rate=tax_rate,
                    expiry_date=exp_date,
                    batch_number=f"BATCH-{today.year}-B{random.randint(10, 99)}",
                    is_active=True,
                )
                products_to_add.append(product_obj)

        if products_to_add:
            db.bulk_save_objects(products_to_add)
            db.commit()

        total_products_count = db.query(Product).count()
        print(f"[OK] Products generated: Added {len(products_to_add)} products.")
        print(f"[OK] Total grocery inventory in database: {total_products_count} items (exceeds requirement of 500+).")
        print("\n" + "=" * 65)
        print("[SUCCESS] Database Seeding Successfully Completed!")
        print(f"Total Users: {db.query(User).count()} (Owner, Manager, Cashier)")
        print(f"Total Suppliers: {db.query(Supplier).count()}")
        print(f"Total Categories: {db.query(Category).count()}")
        print(f"Total Products: {total_products_count} grocery catalog records")
        print("=" * 65)

    except Exception as exc:
        db.rollback()
        print(f"\n[ERROR] Seeding Error: {exc}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
