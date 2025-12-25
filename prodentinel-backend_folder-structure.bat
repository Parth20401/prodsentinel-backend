@echo off
SET PROJECT_NAME=prodsentinel-backend

REM Create root directory
mkdir %PROJECT_NAME%
cd %PROJECT_NAME%

REM Create top-level folders
mkdir app
mkdir alembic

REM Create core folders
mkdir app\core
mkdir app\models
mkdir app\schemas
mkdir app\routers
mkdir app\services
mkdir app\utils

REM Create Python files in app/
type nul > app\main.py
type nul > app\__init__.py

REM Core files
type nul > app\core\config.py
type nul > app\core\logging.py
type nul > app\core\database.py

REM Models
type nul > app\models\base.py
type nul > app\models\raw_signal.py
type nul > app\models\__init__.py

REM Schemas
type nul > app\schemas\signals.py
type nul > app\schemas\common.py
type nul > app\schemas\__init__.py

REM Routers
type nul > app\routers\ingest.py
type nul > app\routers\__init__.py

REM Services
type nul > app\services\ingestion_service.py
type nul > app\services\__init__.py

REM Utils
type nul > app\utils\ids.py
type nul > app\utils\time.py

REM Root-level files
type nul > requirements.txt
type nul > README.md

echo.
echo Project structure "%PROJECT_NAME%" created successfully.
pause
