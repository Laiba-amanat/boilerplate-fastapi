# Quick Start

Welcome to FastAPI Backend Template! This guide will help you quickly set up and run the project.

## System Requirements

- **Python**: 3.11+
- **Operating System**: Windows, macOS, Linux
- **Memory**: Recommended 4GB or more
- **Storage**: At least 1GB available space

## Installation Steps

### 1. Get the Project

```bash
git clone https://github.com/JiayuXu0/FastAPI-Template.git
cd FastAPI-Template
```

### 2. Install UV Package Manager

=== "Linux/macOS"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

=== "Using pip"

    ```bash
    pip install uv
    ```

### 3. Install Dependencies

```bash
# Install project dependencies
uv sync

# Install development dependencies
uv sync --dev
```

### 4. Environment Configuration

Copy the environment configuration file:

```bash
cp .env.example .env
```

Edit the `.env` file and configure necessary environment variables:

```env
# Application Configuration
APP_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database Configuration
DB_ENGINE=sqlite
DB_NAME=fastapi_template.db

# JWT Configuration
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=240
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 5. Initialize Database

```bash
# Initialize database
uv run aerich init-db
```

### 6. Start Service

```bash
# Start in development environment
uv run uvicorn src:app --reload --host 0.0.0.0 --port 8000
```

## Verify Installation

### 1. Check Health Status

```bash
curl http://localhost:8000/api/v1/base/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "environment": "development",
  "service": "FastAPI Backend Template"
}
```

### 2. Access API Documentation

Open your browser and visit the following addresses:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test Login

Login with the default administrator account:

```bash
curl -X POST "http://localhost:8000/api/v1/base/access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "abcd1234"
  }'
```

## Project Structure

```
FastAPI-Template/
├── src/                    # Source code directory
│   ├── api/               # API routing layer
│   │   └── v1/           # API version v1
│   ├── services/         # Business logic layer
│   ├── repositories/     # Data access layer
│   ├── models/           # Data models
│   ├── schemas/          # Data validation schemas
│   ├── core/             # Core functionality
│   ├── utils/            # Utility functions
│   └── main.py           # Application entry point
├── tests/                 # Test files
├── migrations/           # Database migration files
├── docs/                 # Documentation source files
├── .env.example          # Environment variable example
├── pyproject.toml        # Project configuration
└── README.md             # Project description
```

## Common Questions

### Q: How to change the default port?

A: Specify the port in the startup command:

```bash
uv run uvicorn src:app --reload --host 0.0.0.0 --port 8080
```

### Q: How to switch to PostgreSQL?

A: Modify the database configuration in the `.env` file:

```env
DB_ENGINE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fastapi_template
DB_USER=your_username
DB_PASSWORD=your_password
```

### Q: How to reset the database?

A: Delete the database file and migration records:

```bash
# SQLite
rm fastapi_template.db

# Re-initialize
uv run aerich init-db
```

### Q: How to change the default administrator password?

A: Modify it through the user management interface after login, or set it via environment variable on first startup:

```env
DEFAULT_ADMIN_PASSWORD=your_new_password
```

## Next Steps

- 📖 Read [Architecture Design](../architecture/) to understand the system architecture
- 🔧 Check [Development Guide](../development/) to understand development standards
- 📚 Browse [API Documentation](../api/) to understand API usage
- 🚀 Learn [Deployment Guide](../development/deployment.md) for production deployment

## Get Help

If you encounter any issues during use, you can:

1. Visit [Official Website](http://fastapi.infyai.cn/) for the latest documentation
2. Check [FAQ](../faq.md)
3. Search [GitHub Issues](https://github.com/JiayuXu0/FastAPI-Template/issues)
4. Create a new [Issue](https://github.com/JiayuXu0/FastAPI-Template/issues/new)
