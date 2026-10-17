# Grocery Store POS Billing System 🛒

An enterprise-ready, high-speed Point-of-Sale (POS) Billing & Retail Management System designed for modern grocery supermarkets and retail outlets.

---

## 🏗️ Monorepo Architecture

```
Grocery POS/
├── backend/                  # FastAPI REST API (Python 3.11+)
│   ├── app/
│   │   ├── core/             # Configuration, DB connection, security helpers
│   │   ├── models/           # SQLAlchemy models (Product, Customer, Order, OrderItem)
│   │   ├── schemas/          # Pydantic schemas for request/response validation
│   │   ├── routers/          # API routes (products, orders, billing, health)
│   │   ├── __init__.py
│   │   └── main.py           # FastAPI entrypoint with CORS & seed data
│   ├── .env.example
│   ├── Dockerfile            # Container definition for backend
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # React 19 + Vite Billing Terminal
│   ├── src/
│   │   ├── api/              # API services (productsApi, billingApi, client)
│   │   ├── components/       # Header, BarcodeScanner, ProductCatalog, CartPanel, etc.
│   │   ├── context/          # CartContext (cart, pricing totals, cashier state)
│   │   ├── pages/            # POSPage, InventoryPage, TransactionsPage
│   │   ├── App.jsx
│   │   ├── index.css         # Modern POS design system (dark mode, thermal print styles)
│   │   └── main.jsx
│   ├── Dockerfile            # Multi-stage Dockerfile (Node build + Nginx serve)
│   ├── nginx.conf            # Nginx reverse proxy configuration
│   └── package.json
│
├── desktop/                  # Electron Desktop Wrapper
│   ├── main.js               # Main Electron process (kiosk mode, receipt printer IPC)
│   ├── preload.js            # Secure contextBridge API for React frontend
│   ├── package.json
│   └── .gitignore
│
├── docker-compose.yml        # Orchestration for PostgreSQL, Backend, and Frontend
├── .gitignore                # Root gitignore (Node, Python, Electron, DB, OS)
├── package.json              # Root workspace convenience scripts
└── README.md
```

---

## 🚀 Quick Start Guide

### Option 1: Full-Stack with Docker Compose (Recommended)

Start PostgreSQL, the FastAPI backend, and the React frontend in containers:

```bash
docker-compose up --build
```

- **Frontend Terminal**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger)**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **PostgreSQL Database**: Port `5432` (`grocery_pos`)

---

### Option 2: Local Development Setup

#### 1. Backend (FastAPI)
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173).

#### 3. Desktop Application (Electron)
```bash
cd desktop
npm install
npm start
```
*Note: Make sure the frontend dev server is running on port 5173 or run `npm run build` in `frontend`.*

---

## ⚡ Core Features (Phase 1 & 2)

- **High-Speed Barcode Scanning**: Instant lookup with Enter key, quick barcode simulation buttons, and audio-visual scan flash.
- **Dynamic Real-Time Billing**: Automatic subtotal, GST/tax computation, discount rules (% or fixed ₹), and grand total calculation.
- **Tender & Change Calculator**: Real-time cash return calculation with quick bill denomination buttons.
- **Thermal Receipt Printing**: Printable 80mm slip format with itemized charges, GST summary, and printable barcode compatible with thermal POS printers and Electron.
- **Inventory & Stock Management**: Real-time inventory tracking, unit measurements (`kg`, `pcs`, `pack`), and new item registration.
- **Sales History & Reprints**: Searchable invoice log with reprint capabilities.
