# Grocery Mart POS

Full-stack grocery retail management software for billing, inventory, purchasing, sales history, returns, reporting, and store administration.

The project provides a browser-based React terminal and an Electron desktop terminal backed by a FastAPI REST API.

![React](https://img.shields.io/badge/React-19-149ECA?style=flat-square&logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)
![Electron](https://img.shields.io/badge/Electron-Desktop-47848F?style=flat-square&logo=electron&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## Features

- Fast grocery billing terminal with barcode entry, product search, cart management, taxes, payments, and receipts.
- Sales history with return and refund processing.
- Inventory catalog with stock quantities, low-stock alerts, expiry dates, cost price, retail price, margins, and valuation.
- 658 seeded grocery products for demonstrations and development.
- Product cards with barcode-based product-image lookup and category photo fallback.
- Supplier directory, purchase orders, receiving, and stock replenishment.
- Owner reports for sales, best-selling products, inventory margins, and audit data.
- Store settings, GST/receipt settings, and owner-only staff management.
- Motion-enhanced React interface and Electron desktop wrapper.
- SQLite fallback for local development when PostgreSQL is unavailable.

## Role permissions

| Role | Access |
|---|---|
| Owner | Full access, reports, settings, staff management, inventory, purchasing, billing, sales history, and returns |
| Manager | Inventory, catalog, suppliers, purchase orders, billing, sales history, and returns |
| Terminal Cashier | Billing Terminal, Sales History, and returns/refunds only |

Terminal Cashiers cannot open Dashboard, Inventory, Suppliers, Reports, or Store Settings.

## Technology stack

- Frontend: React 19, Vite, JavaScript, CSS, Recharts, Lucide React
- Backend: Python, FastAPI, SQLAlchemy, Pydantic, Alembic
- Desktop: Electron
- Database: PostgreSQL when configured, SQLite fallback for local development
- Containers: Docker Compose

## Project structure

```text
Grocery-Mart/
├── README.md
├── .gitignore
└── Grocery POS/
    ├── backend/       FastAPI API, models, routers, migrations, and seed data
    ├── frontend/      React/Vite application
    ├── desktop/       Electron application wrapper and packaging scripts
    ├── docker-compose.yml
    ├── package.json
    └── package-lock.json
```

## Demo accounts

| Username | Password | Role |
|---|---|---|
| `owner` | `password123` | Owner |
| `manager` | `password123` | Manager |
| `cashier1` | `password123` | Terminal Cashier |

Change all demo credentials before using the application in a real store.

## Local setup

### Prerequisites

- Git
- Python 3.12 or newer supported by the backend dependencies
- Node.js and npm
- Docker Desktop (optional)

### Backend

From the repository root:

```powershell
cd "Grocery POS\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

For a browser development session, start the API on port `8000`:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

For the packaged Electron desktop build, the frontend is configured to use port `8001`:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

API documentation is available at `/docs`, for example `http://127.0.0.1:8000/docs`.

The application initializes the local catalog and seeds more than 650 grocery products when using the SQLite fallback.

### Web frontend

Open a second terminal:

```powershell
cd "Grocery POS"
npm install
npm run dev:frontend
```

Open the Vite URL printed in the terminal. The browser development frontend uses the backend on port `8000`.

### Electron desktop

Build the frontend and copy it into the Electron app:

```powershell
cd "Grocery POS"
npm run build:frontend
```

Start the desktop terminal while the backend is running on port `8001`:

```powershell
npm run dev:desktop
```

Create a Windows installer or portable build:

```powershell
npm run build:desktop
```

Generated desktop packages are written to `Grocery POS/desktop/dist-electron`.

### Docker

From the `Grocery POS` directory:

```powershell
docker compose up --build
docker compose down
```

## Useful commands

Run these from `Grocery POS`:

```powershell
npm run dev:frontend     # Start Vite
npm run build:frontend   # Build React into frontend/dist
npm run dev:desktop      # Start Electron
npm run build:desktop    # Build frontend and Windows Electron package
npm run docker:up        # Start Docker services
npm run docker:down      # Stop Docker services
```

## Configuration and security

- Keep secrets in `backend/.env`; never commit real credentials or tokens.
- Use a strong JWT secret outside local demonstrations.
- Use PostgreSQL for production instead of the local SQLite fallback.
- Keep the API and desktop client on the intended local ports.
- Staff removal deactivates the account and preserves its sales and return history.
- Product photos may use internet-based sources; local category visuals remain available when the network is offline.

## Troubleshooting

### Dashboard or metrics show HTTP 500 / Failed to fetch

1. Confirm the backend is running.
2. Use port `8000` for the Vite browser session and port `8001` for packaged Electron.
3. Make sure another process is not already using the selected port.
4. Restart the backend after changing backend routes.

### Electron shows a blank page

Rebuild the frontend bundle and restart Electron:

```powershell
cd "Grocery POS"
npm run build:frontend
```

### Staff changes do not appear

Sign in as Owner, open **Store Settings → Staff & User Roles**, and refresh the application after restarting the backend if a new API route was added.

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-change`.
3. Make and test your changes.
4. Commit with a descriptive message.
5. Push the branch and open a pull request.

## License

This project is licensed under the MIT License.

## Repository

[github.com/vikas468368-star/Grocery-Mart](https://github.com/vikas468368-star/Grocery-Mart)
