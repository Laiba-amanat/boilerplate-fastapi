# Frequently Asked Questions

## 🚀 Quick Start

### Q: What to do when encountering errors during dependency installation?

A: Please ensure you are using Python 3.11+ and have a stable network connection. If you encounter package conflicts, you can try:

```bash
# Clear cache
uv cache clean

# Reinstall
uv sync --reinstall
```

### Q: How to change the default port?

A: Specify the port in the startup command:

```bash
uv run uvicorn src:app --reload --host 0.0.0.0 --port 8080
```

Or set it in the `.env` file:

```env
PORT=8080
```

### Q: What is the default administrator account?

A: Default administrator account:
- Username: `admin`
- Password: `abcd1234`

**Important**: Please change the default password immediately in production environment!

## 🔧 Configuration Related

### Q: How to switch databases?

A: Modify the database configuration in the `.env` file:

=== "PostgreSQL"

    ```env
    DB_ENGINE=postgres
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=fastapi_template
    DB_USER=your_username
    DB_PASSWORD=your_password
    ```

=== "SQLite"

    ```env
    DB_ENGINE=sqlite
    DB_NAME=fastapi_template.db
    ```

### Q: How to configure CORS?

A: Set allowed origins in the `.env` file:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://yourdomain.com
```

### Q: How to change JWT expiration time?

A: Configure in the `.env` file:

```env
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=240  # Access token 4 hours
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7      # Refresh token 7 days
```

## 🗄️ Database Related

### Q: How to reset the database?

A: Delete the database file and re-initialize:

```bash
# SQLite
rm fastapi_template.db

# Delete migration records
rm -rf migrations/

# Re-initialize
uv run aerich init-db
```

### Q: How to add a new data table?

A: Follow these steps:

1. Define model in `src/models/`
2. Generate migration file
3. Apply migration

```bash
# Generate migration
uv run aerich migrate --name "add_new_table"

# Apply migration
uv run aerich upgrade
```

### Q: What to do if migration fails?

A: Check migration history and manually fix:

```bash
# View migration history
uv run aerich history

# If rollback is needed
uv run aerich downgrade

# Re-migrate after manual fix
uv run aerich migrate --name "fix_migration"
uv run aerich upgrade
```

## 🔐 Authentication & Authorization

### Q: How to add a new user role?

A: Add via API or directly in the database:

```python
# Add via code
from src.models.admin import Role

role = await Role.create(
    name="editor",
    description="Editor role"
)
```

### Q: How to customize permission checks?

A: Create custom dependency:

```python
from fastapi import Depends, HTTPException
from src.core.dependency import get_current_user

def require_admin(current_user = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin permission required")
    return current_user
```

### Q: How to handle JWT token expiration?

A: Use refresh token to get new access token:

```python
# Use refresh token
response = requests.post("/api/v1/base/refresh_token", json={
    "refresh_token": "your_refresh_token"
})
```

## 📁 File Management

### Q: How to limit file upload size?

A: Modify in `src/services/file_service.py`:

```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

### Q: How to add support for new file types?

A: Modify the allowed file types list:

```python
ALLOWED_EXTENSIONS = {
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
    'document': ['.pdf', '.doc', '.docx', '.txt'],
    'video': ['.mp4', '.avi', '.mkv']  # Add video support
}
```

### Q: Where are uploaded files stored?

A: Default storage is in the `uploads/` directory, can be modified via environment variable:

```env
UPLOAD_DIR=/path/to/uploads
```

## 🧪 Testing Related

### Q: How to run tests?

A: Use pytest to run tests:

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_users.py

# Run tests with coverage
uv run pytest --cov=src --cov-report=html
```

### Q: How to add new tests?

A: Create test file in `tests/` directory:

```python
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/users/create", json={
            "username": "testuser",
            "password": "password123"
        })
    assert response.status_code == 200
```

## 🚀 Deployment Related

### Q: How to deploy to production environment?

A: Deploy using Docker:

```bash
# Build image
docker build -t fastapi-template .

# Run container
docker run -d -p 8000:8000 --name fastapi-app fastapi-template
```

### Q: How to configure reverse proxy?

A: Nginx configuration example:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Q: How to set environment variables?

A: Production environment recommends using environment variables instead of `.env` file:

```bash
export SECRET_KEY="your-secret-key"
export DB_HOST="your-db-host"
export DB_PASSWORD="your-db-password"
```

## 🐛 Troubleshooting

### Q: What to do when application startup reports errors?

A: Check the following items:

1. Ensure all dependencies are installed
2. Check database connection configuration
3. Verify environment variable settings
4. View detailed error logs

```bash
# View detailed logs
uv run uvicorn src:app --reload --log-level debug
```

### Q: Database connection failed?

A: Check database configuration and connection:

```python
# Test database connection
from src.core.database import get_db_connection

async def test_db():
    try:
        conn = await get_db_connection()
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
```

### Q: How to enable debug mode?

A: Set in the `.env` file:

```env
DEBUG=True
APP_ENV=development
```

## 📚 Development Related

### Q: How to add a new API endpoint?

A: Add following the three-layer architecture:

1. Define model (`src/models/`)
2. Create repository (`src/repositories/`)
3. Implement service (`src/services/`)
4. Add route (`src/api/v1/`)

### Q: How to customize middleware?

A: Add in `src/core/middleware.py`:

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Process before request
        response = await call_next(request)
        # Process after response
        return response
```

### Q: How to add scheduled tasks?

A: Use APScheduler:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job("interval", minutes=30)
async def cleanup_expired_tokens():
    # Clean up expired tokens
    pass

scheduler.start()
```

## 🔍 Performance Optimization

### Q: How to optimize database queries?

A: Use the following techniques:

1. Use `select_related()` to preload related data
2. Use `prefetch_related()` to optimize many-to-many queries
3. Add appropriate database indexes
4. Use query pagination

```python
# Preload related data
users = await User.all().select_related("roles")

# Batch preload
users = await User.all().prefetch_related("roles__permissions")
```

### Q: How to add caching?

A: Use Redis caching:

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args)+str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## 📞 Get Help

If the above FAQ doesn't solve your problem, you can:

1. Visit [Official Website](http://fastapi.infyai.cn/) for the latest documentation
2. Check [GitHub Issues](https://github.com/JiayuXu0/FastAPI-Template/issues)
3. Create a new [Issue](https://github.com/JiayuXu0/FastAPI-Template/issues/new)
4. Check other parts of the project documentation

## 🤝 Contributing Guide

If you discover new issues or have improvement suggestions, welcome to:

1. Submit Issue to report problems
2. Submit PR to improve documentation
3. Participate in discussions and code reviews

Thank you for your contribution!
