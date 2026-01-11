# ProdSentinel Backend - Implementation & Troubleshooting Guide

This document captures key technical challenges encountered during the development of the ProdSentinel Ingestion API and their resolutions. It serves as a knowledge base for future maintenance and debugging.

## 1. Database & ORM Issues

### Issue: Health Check SQL Compatibility
**Symptoms**: The health check endpoint `GET /ingest/health` failed with:
`Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')`

**Context**: SQLAlchemy 2.0+ deprecated the usage of raw string SQL with `session.execute()`.

**Solution**:
All raw SQL queries must be wrapped in `sqlalchemy.text()`.

```python
from sqlalchemy import text

# Incorrect
await db.execute("SELECT 1")

# Correct
await db.execute(text("SELECT 1"))
```

### Issue: `asyncpg` DSN Format Incompatibility
**Symptoms**: Verification scripts failed with:
`invalid DSN: scheme is expected to be either "postgresql" or "postgres", got 'postgresql+asyncpg'`

**Context**:
- SQLAlchemy requires the driver specification: `postgresql+asyncpg://...`
- `asyncpg` (the underlying driver) requires standard DSN: `postgresql://...`

**Solution**:
The application configuration maintains the SQLAlchemy format for the ORM. External scripts or direct driver usage must normalize the DSN string:

```python
# Convert SQLAlchemy DSN to asyncpg format
connection_dsn = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
```

---

## 2. Serialization & Validation

### Issue: Pydantic V2 JSON Serialization
**Symptoms**: Ingestion requests failed with `500 Internal Server Error` and logs showed:
`TypeError: Object of type UUID is not JSON serializable`

**Context**:
Pydantic V2's `.model_dump()` returns native Python objects (UUID, datetime, Enum) by default. SQLAlchemy's JSON column type expects fully serialized JSON-compatible primitive types (strings, ints).

**Solution**:
Explicitly request JSON-mode serialization when preparing payloads for JSON database columns:

```python
# Incorrect (Returns native objects)
payload = signal.model_dump()

# Correct (Returns strings for UUIDs, ISO strings for datetimes)
payload = signal.model_dump(mode='json')
```

---

## 3. Integration Patterns

### Issue: Service Telemetry Integration
**Symptoms**: Fake services were running but no logs appeared in the backend. 
Errors included `404 Not Found` (wrong port) and `TimeoutError`.

**Context**:
- Microservices need a non-blocking way to emit telemetry.
- Telemetry failure should not crash the main application flow.

**Solution**:
1. **Fire-and-Forget Pattern**: Use `asyncio.create_task()` to offload telemetry sending.
2. **Configuration**: Externalize backend URLs via environment variables (`PRODSENTINEL_URL`).
3. **Resilience**: Short timeouts (0.5s - 2.0s) and silent failure handling for the telemetry sender to prevent cascading failures.

```python
# Implementation Pattern
asyncio.create_task(send_log_to_prodsentinel(...))
```

---

## 4. Verification

### End-to-End Testing Script
A verification script `verify_integration.py` is located in `prodsentinel-fake-services/scripts/`. 
It performs the following checks:
1. Pings the Backend Health Check
2. Triggers a transaction on the API Gateway
3. Verifies the logs were actually written to the Postgres database

**Usage**:
```bash
python scripts/verify_integration.py
```

---

## 5. Migration Challenges

### Issue: Alembic Async vs Sync Execution
**Symptoms**: Database migrations appeared to complete successfully (recorded in `alembic_version`), but tables were **never created**. Logs showed a `RuntimeWarning: coroutine ... was never awaited`.

**Context**: 
While the application uses an Async engine (`asyncpg`), Alembic's migration scripts themselves must adhere to a specific execution model. Mistakenly defining the `upgrade()` wrapper as `async` or failing to bridge the context correctly causes it to be skipped by the runner.

**Solution**:
The migration environment (`env.py`) must create an async engine but execute the actual migration steps synchronously within a `connection.run_sync()` context.

```python
# Incorrect (Async Logic in Migration)
async def run_migrations_online():
    connectable = AsyncEngine(...)
    async with connectable.connect() as connection:
        await context.run_migrations()  # ❌ Fails silently

# Correct (Bridging Async to Sync)
def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = create_async_engine(...)
    
    async with connectable.connect() as connection:
        # ✅ Bridges to sync execution
        await connection.run_sync(do_run_migrations)
```

**Key Takeaway**: Schema management must be explicit. Never rely on runtime table creation (`Base.metadata.create_all`) in production async applications; always use versioned migrations.
