# SmartCache AI

## 1. Project Name
**SmartCache AI**

## 2. Project Objective
**Adaptive Application-Aware Cache Management System** — An intelligent caching platform foundation designed to optimize data caching decisions based on dynamic application context and traffic.

## 3. Technology Stack
- **Frontend**:
  - React
  - Vite
  - Tailwind CSS
- **Backend**:
  - Python 3.11+
  - FastAPI
  - Uvicorn
  - Pydantic
  - python-dotenv
  - Pytest
  - HTTPX
- **Infrastructure**:
  - Redis
  - PostgreSQL
  - Docker Compose

## 4. Project Structure
```text
smartcache-ai/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   │
│   ├── tests/
│   │   └── test_health.py
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── .env.example
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 5. How to Run Locally

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
5. Start the backend:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
6. Run tests:
   ```bash
   pytest
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
4. Start the frontend development server:
   ```bash
   npm run dev
   ```

## 6. How to Run with Docker

1. Ensure Docker and Docker Compose are installed and running.
2. From the project root, build and start all services:
   ```bash
   docker-compose up --build
   ```
   Or in detached mode:
   ```bash
   docker-compose up -d --build
   ```
3. To stop all services:
   ```bash
   docker-compose down
   ```

## 7. Backend URL
- [http://localhost:8000](http://localhost:8000)

## 8. Frontend URL
- [http://localhost:5173](http://localhost:5173)

## 9. FastAPI Swagger URL
- [http://localhost:8000/docs](http://localhost:8000/docs)
