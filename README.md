# ScoutLab Analytics ⚽📈

ScoutLab is a full-stack analytics platform for Sorare managers. It provides real-time market data, portfolio valuation, advanced player scouting, and automated alerts, powered by the official Sorare GraphQL and WebSocket APIs.

## 🚀 Features

*   **Real-time Market Data:** Automatically syncs live auctions and offers using Sorare's ActionCable WebSockets.
*   **Advanced Scouting:** Filter and search the entire player database with custom weights for form, consistency, fixtures, and more.
*   **Portfolio Valuation:** Instantly calculate the value of your gallery based on real-time market data.
*   **Alerts & Watchlists:** Track specific players and get notified when they hit your target price or score thresholds.
*   **Interactive Dashboards:** Beautiful, responsive UI built with modern React components and interactive charts.

## 🛠️ Tech Stack

**Frontend**
*   [React 19](https://react.dev/) + [Vite](https://vitejs.dev/)
*   [TanStack Router](https://tanstack.com/router) & [React Query](https://tanstack.com/query)
*   [Tailwind CSS v4](https://tailwindcss.com/) & [shadcn/ui](https://ui.shadcn.com/) (Radix)

**Backend**
*   [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
*   [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async)
*   [Redis](https://redis.io/) (Caching & WebSocket Pub/Sub)
*   [PostgreSQL](https://www.postgresql.org/) (Production DB) / SQLite (Local Dev DB)

**Infrastructure**
*   Docker & Docker Compose
*   Nginx (Frontend proxy)

---

## 🏗️ Getting Started (Docker / Production)

The easiest way to run ScoutLab is using the provided Docker Compose configuration, which automatically orchestrates the Database (Postgres), Cache (Redis), Backend API, Background Worker, and Frontend (Nginx).

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/scoutlab.git
   cd scoutlab
   ```

2. Copy the example environment file and add your Sorare credentials:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env to include your SORARE_JWT (or run get_jwt.py)
   ```

3. Build and launch the stack:
   ```bash
   docker-compose up -d --build
   ```

4. Access the application:
   * **Frontend Dashboard:** [http://localhost](http://localhost)
   * **API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💻 Local Development (Native)

If you prefer to run the services natively without Docker for development:

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Activate venv: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
pip install -r requirements.txt

# Run the backend (defaults to SQLite + in-memory cache if Postgres/Redis aren't running)
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install --legacy-peer-deps

# Create local env file to point to the backend
echo "VITE_API_BASE_URL=http://127.0.0.1:8000" > .env.local

# Run the dev server
npm run dev
```
Navigate to `http://localhost:5173` (or the port Vite outputs) to see the app.

---

## 🔑 Authentication (Sorare API)

To pull live data, ScoutLab requires a valid Sorare JWT. 
A helper script is provided to generate this token securely using your credentials (they are hashed locally and never stored):

```bash
cd backend
python get_jwt.py
```
This script will automatically inject the retrieved token into your `.env` file.

## 📄 License

This project is licensed under the MIT License. Data provided by the Sorare API belongs to Sorare.
