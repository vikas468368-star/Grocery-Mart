# Grocery-Mart | Retail Point of Sale System

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=220&color=0:0F172A,30:2563EB,65:7C3AED,100:06B6D4&text=Grocery-Mart&fontColor=FFFFFF&fontSize=54&fontAlignY=38&animation=twinkling&desc=Smart%20Retail%20Management%20%7C%20Billing%20%7C%20Inventory&descAlignY=60&descSize=16" width="100%" alt="Grocery-Mart colorful animated banner"/>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=500&size=20&duration=3000&pause=900&color=38BDF8&center=true&vCenter=true&width=750&lines=Modern+Grocery+Billing+System;Inventory+and+Product+Management;React+%2B+FastAPI+%2B+Electron;Built+for+Modern+Retail+Workflows" alt="Animated project introduction"/>

<br/>

[![Repository](https://img.shields.io/badge/GitHub-Grocery--Mart-181717?style=for-the-badge&logo=github)](https://github.com/vikas468368-star/Grocery-Mart)
[![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Desktop](https://img.shields.io/badge/Desktop-Electron-47848F?style=for-the-badge&logo=electron&logoColor=white)](https://www.electronjs.org/)

**A modern retail management project designed to bring billing, inventory, sales operations, and desktop application support into one organized system.**

[Explore the Project](https://github.com/vikas468368-star/Grocery-Mart/tree/main/Grocery%20POS) · [Report an Issue](https://github.com/vikas468368-star/Grocery-Mart/issues) · [Contribute](https://github.com/vikas468368-star/Grocery-Mart/pulls)

</div>

---

## About the Project

**Grocery-Mart** is a grocery store and supermarket Point of Sale (POS) project focused on simplifying retail operations through a structured software architecture.

The project separates the user interface, backend API, and desktop application into dedicated components. This structure helps developers maintain the codebase, extend existing functionality, and develop new features more efficiently.

The source code is located in the `Grocery POS` directory of this repository.

### Project Goals

- Simplify checkout and billing workflows.
- Organize product and inventory management.
- Support customer, supplier, and sales-related operations.
- Provide a React-based user interface.
- Expose backend functionality through a FastAPI application.
- Support a desktop application through Electron.
- Provide Docker configuration for containerized development.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, JavaScript, Vite |
| Styling | CSS, Tailwind CSS configuration |
| Backend | Python, FastAPI |
| API Documentation | FastAPI interactive API documentation |
| Database Layer | Backend database configuration and SQLAlchemy-related migrations |
| Database Migrations | Alembic |
| Desktop Application | Electron, JavaScript |
| Containerization | Docker, Docker Compose |
| Package Management | npm, pip |

## Core Modules

The source code is organized around the following application areas.

### Point of Sale and Billing

- Billing-related API endpoints.
- Cart and checkout interface components.
- Receipt and checkout modal components.
- Barcode scanner component.
- Sales and transaction-related workflows.

### Product and Inventory Management

- Product and category API modules.
- Product catalog interface.
- Inventory management page.
- Product selection and product details components.

### Customers and Suppliers

- Customer data models and API routes.
- Supplier data models and API routes.
- Supplier management interface.
- Customer-related backend schemas.

### Reports and Administration

- Reports API and reporting interface.
- Settings page.
- User and authentication modules.
- Orders, payments, and returns API modules.

> The availability and completeness of individual features should be verified against the current implementation before using the application in a live retail environment.

## Architecture

```text
Grocery-Mart
|
+-- Grocery POS/
    |
    +-- frontend/
    |   +-- src/
    |   |   +-- api/
    |   |   +-- components/
    |   |   +-- context/
    |   |   +-- hooks/
    |   |   +-- pages/
    |   +-- package.json
    |
    +-- backend/
    |   +-- app/
    |   |   +-- core/
    |   |   +-- models/
    |   |   +-- routers/
    |   |   +-- schemas/
    |   +-- alembic/
    |   +-- requirements.txt
    |
    +-- desktop/
    |   +-- main.js
    |   +-- preload.js
    |   +-- package.json
    |
    +-- docker-compose.yml
    +-- package.json
    +-- README.md
```

### How the Components Work Together

1. The React frontend provides the user interface.
2. The frontend API modules communicate with the backend.
3. FastAPI exposes routes for application operations.
4. Backend models and database configuration support data management.
5. Alembic manages database schema migrations.
6. Electron provides the desktop application runtime.
7. Docker configuration supports container-based development.

## Getting Started

Follow the instructions below to prepare the project for local development.

### Prerequisites

Install the following tools before starting:

- [Git](https://git-scm.com/downloads)
- [Python](https://www.python.org/downloads/)
- [Node.js and npm](https://nodejs.org/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — optional, for container-based workflows

### 1. Clone the Repository

```bash
git clone https://github.com/vikas468368-star/Grocery-Mart.git
cd Grocery-Mart
cd "Grocery POS"
```

### 2. Configure the Backend

Open a terminal inside the `Grocery POS` directory.

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```bash
pip install -r backend/requirements.txt
```

If the backend requires environment variables, create a local configuration file from the provided example:

```powershell
Copy-Item backend/.env.example backend/.env
```

Review the environment variables and configure them for your machine. Do not commit real passwords, API keys, or secret values.

Start the backend from the `Grocery POS` directory:

```bash
python -m uvicorn app.main:app --reload --app-dir backend
```

If startup succeeds with the default Uvicorn port, visit:

- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

Database configuration and migrations may need to be completed before all endpoints can be used.

### 3. Start the Frontend

Open a second terminal:

```bash
cd "Grocery POS/frontend"
npm install
npm run
```

The last command lists the scripts defined in `package.json`. Run the development script shown there, commonly:

```bash
npm run dev
```

Use the local URL displayed by Vite in the terminal. Ensure the frontend API configuration points to the backend address.

### 4. Run the Desktop Application

Open a separate terminal:

```bash
cd "Grocery POS/desktop"
npm install
npm run
```

Review the available scripts before launching the desktop application or building an installer. The exact command depends on the scripts configured in the desktop package.

### 5. Docker

The project includes a `docker-compose.yml` file. Review its service configuration and required environment variables before starting the containers.

From the `Grocery POS` directory, use:

```bash
docker compose config
```

If the configuration validates and the required environment is ready:

```bash
docker compose up --build
```

## Development Guidelines

To keep the project maintainable:

- Keep frontend components focused on their individual responsibilities.
- Keep backend routes, models, schemas, and configuration organized.
- Store secrets in local environment files rather than source control.
- Exclude build outputs, dependencies, caches, and local database files from Git.
- Validate database migrations before applying them to important data.
- Test billing, inventory updates, and payment workflows before releasing changes.

## Current Project Status

**Development status: In progress.**

The repository contains the frontend, backend, and desktop application source structure. Production readiness, end-to-end integration, automated test coverage, and deployment security should be verified before the software is used by a business.

## Roadmap

Potential areas for continued development include:

- End-to-end testing of the checkout process.
- Inventory validation and low-stock alerts.
- Improved reporting and sales summaries.
- Robust authentication and authorization.
- Reliable database backup and recovery.
- Automated tests for critical billing operations.
- Desktop packaging and release automation.
- Production deployment documentation.

## Contributing

Contributions, suggestions, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch.

   ```bash
   git checkout -b feature/your-feature
   ```

3. Make and test your changes.
4. Commit your work.

   ```bash
   git add .
   git commit -m "Add your feature"
   ```

5. Push your branch.

   ```bash
   git push origin feature/your-feature
   ```

6. Open a pull request describing your changes.

## License

No license has been specified in this README. Add a `LICENSE` file and update this section when the project's licensing terms have been decided.

## Author

**Vikas Madheshiya**

GitHub: [@vikas468368-star](https://github.com/vikas468368-star)

Project repository: [Grocery-Mart](https://github.com/vikas468368-star/Grocery-Mart)

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:06B6D4,50:2563EB,100:0F172A&height=120&section=footer" width="100%" alt="Colorful gradient footer"/>

**Grocery-Mart**

*Building organized, maintainable retail software.*

</div>
