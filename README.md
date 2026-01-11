# ProdSentinel Backend

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791?style=for-the-badge&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**ProdSentinel Backend** is the high-performance ingestion and query engine for the ProdSentinel incident analysis platform. It is designed to handle high-velocity telemetry streams (logs, traces, metrics) with strict reliability guarantees, utilizing an async-first architecture to ensure non-blocking signal acceptance.

## 🚀 Key Features

*   **⚡ Async-First Architecture**: Built on `FastAPI` and `SQLAlchemy (AsyncPG)` for maximum throughput.
*   **🛡️ Immutable Event Store**: All incoming signals are stored in an append-only `raw_signals` table to ensure data integrity.
*   **🔄 Idempotency Guarantee**: Unique `signal_id` enforcement prevents duplicate processing of telemetry.
*   **🔍 Structured Correlation**: Native support for `trace_id` propagation for distributed tracing analysis.
*   **✅ Strict Schema Validation**: `Pydantic` models ensure only valid telemetry is persisted.

## 🏗️ Architecture

The backend serves as the bridge between distributed services and the analysis pipeline.

```mermaid
graph LR
    Client[Client Services] -->|HTTP POST| API[Ingestion API]
    API -->|Validate| Schema[Pydantic Schema]
    Schema -->|Valid| DB[(PostgreSQL\nRaw Signals)]
    Schema -->|Invalid| 422[422 Error]
    DB -.->|Poll/CDC| Pipeline[Analysis Pipeline]
    
    style API fill:#009688,stroke:#333,stroke-width:2px,color:white
    style DB fill:#336791,stroke:#333,stroke-width:2px,color:white
    style Client fill:#f9f9f9,stroke:#333
```

### Directory Structure

```text
app/
├── core/           # ⚙️ Config, DB setup, Logging
├── models/         # 🗄️ SQLAlchemy ORM Models
├── routers/        # 🛣️ API Route Handlers
├── schemas/        # 📝 Pydantic Validation Schemas
├── services/       # 🧠 Business Logic
└── utils/          # 🛠️ Helper Utilities
```

## 🛠️ Getting Started

### Prerequisites

*   **Python 3.11+**
*   **PostgreSQL 14+**
*   **Virtual Environment Tool** (venv, etc.)

### Installation

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone https://github.com/yourusername/prodsentinel-backend.git
    cd prodsentinel-backend
    ```

2.  **Create and activate virtual environment**:
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # Linux/Mac
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/prodsentinel
    APP_ENV=development
    LOG_LEVEL=INFO
    ```

5.  **Run Database Migrations**:
    ```bash
    alembic upgrade head
    ```

### Running the Server

Start the development server with auto-reload enabled:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at [http://localhost:8000](http://localhost:8000).

*   **Interactive Docs (Swagger UI)**: [/docs](http://localhost:8000/docs)
*   **ReDoc**: [/redoc](http://localhost:8000/redoc)

## 📡 API Endpoints

### Ingestion API

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/ingest/logs` | Ingest log signals from services. |
| `POST` | `/ingest/traces` | Ingest distributed trace spans. |
| `POST` | `/ingest/metrics` | Ingest application metrics. |

#### Example: Ingest a Log

```bash
curl -X POST "http://localhost:8000/ingest/logs" \
     -H "Content-Type: application/json" \
     -d '{
           "signal_id": "550e8400-e29b-41d4-a716-446655440000",
           "trace_id": "trace-12345",
           "service_name": "payment-service",
           "timestamp": "2026-01-12T10:00:00Z",
           "level": "ERROR",
           "message": "Payment gateway timeout",
           "attributes": {"amount": 500, "currency": "USD"}
         }'
```

## 👩‍💻 Development

### Database Migrations (Alembic)

*   **Create Migration**: `alembic revision --autogenerate -m "migration_name"`
*   **Apply Migration**: `alembic upgrade head`
*   **Rollback**: `alembic downgrade -1`

### Best Practices

*   **Idempotency**: Always generate a UUID for `signal_id` on the client side.
*   **Async**: All I/O bound operations must be `await`able.

## 🤝 Contributing

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request
