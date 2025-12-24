# FastAPI Backend Template

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Ready to Use**

    ---

    Enterprise FastAPI backend template with built-in three-layer architecture design, providing complete RBAC permission management system

    [:octicons-arrow-right-24: Quick Start](guide/)

-   :material-account-group:{ .lg .middle } **User Management**

    ---

    Complete user management system, supporting user registration, login, permission control and other functions

    [:octicons-arrow-right-24: User Management](api/users.md)

-   :material-shield-check:{ .lg .middle } **Permission Control**

    ---

    Role-based access control (RBAC), supporting fine-grained permission management

    [:octicons-arrow-right-24: Permission System](api/roles.md)

-   :material-database:{ .lg .middle } **Database**

    ---

    Based on Tortoise ORM, supporting PostgreSQL and SQLite, including complete migration system

    [:octicons-arrow-right-24: Database Design](architecture/database.md)

</div>

## Project Features

### 🏗️ Architecture Design

- **Three-Layer Architecture**: API → Service → Repository → Model
- **Dependency Injection**: Based on FastAPI dependency system
- **Async Support**: Fully asynchronous design, supporting high concurrency
- **Type Safety**: Complete Python type annotations

### 🔐 Security Features

- **JWT Authentication**: Access token (4 hours) + Refresh token (7 days)
- **RBAC Permissions**: Role-based access control
- **Password Security**: Argon2 hashing algorithm
- **Rate Limiting**: Login frequency limiting

### 📁 Core Features

- **User Management**: User CRUD, password reset, status management
- **Role Management**: Role assignment, permission binding
- **Menu Management**: Dynamic menu configuration
- **File Management**: Secure file upload and download
- **Audit Logging**: Complete operation records
- **Department Management**: Organizational structure management

### 🛠️ Development Tools

- **UV Package Management**: Fast Python package manager
- **Code Standards**: Black + Ruff + MyPy
- **Test Coverage**: Pytest + async testing
- **Database Migration**: Aerich migration tool
- **API Documentation**: Auto-generated OpenAPI documentation

## Tech Stack

=== "Backend Framework"

    - **FastAPI**: Modern, high-performance web framework
    - **Tortoise ORM**: Asynchronous ORM framework
    - **Pydantic**: Data validation and settings management
    - **JWT**: JSON Web Token authentication

=== "Database"

    - **PostgreSQL**: Recommended for production environment
    - **SQLite**: Default for development environment
    - **Redis**: Cache and session storage
    - **Aerich**: Database migration tool

=== "Development Tools"

    - **UV**: Python package manager
    - **Black**: Code formatting
    - **Ruff**: Code checking
    - **MyPy**: Type checking
    - **Pytest**: Testing framework

=== "Deployment & Operations"

    - **Docker**: Containerized deployment
    - **GitHub Actions**: CI/CD automation
    - **Uvicorn**: ASGI server
    - **Nginx**: Reverse proxy

## Quick Start

```bash
# Clone project
git clone https://github.com/JiayuXu0/FastAPI-Template.git
cd FastAPI-Template

# Install dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# Initialize database
uv run aerich init-db

# Start development server
uv run uvicorn src:app --reload --host 0.0.0.0 --port 8000
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to view the interactive API documentation.

## Documentation Navigation

<div class="grid cards" markdown>

-   [:material-book-open-page-variant:{ .lg .middle } **Quick Start**](guide/)

    Project installation, configuration and running guide

-   [:material-library-outline:{ .lg .middle } **Architecture Design**](architecture/)

    System architecture, design patterns and best practices

-   [:material-api:{ .lg .middle } **API Documentation**](api/)

    Complete API interface documentation and usage examples

-   [:material-code-braces:{ .lg .middle } **Development Guide**](development/)

    Development environment configuration and coding standards

</div>

## Contributing

Welcome to contribute to the project! Please refer to the following steps:

1. Fork the project repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License. For details, please refer to the [LICENSE](https://github.com/JiayuXu0/FastAPI-Template/blob/main/LICENSE) file.

## Contact Us

- **🌐 Official Website**: [http://fastapi.infyai.cn/](http://fastapi.infyai.cn/)
- **GitHub**: [JiayuXu0/FastAPI-Template](https://github.com/JiayuXu0/FastAPI-Template)
- **Issues**: [Issue Feedback](https://github.com/JiayuXu0/FastAPI-Template/issues)

---

<p align="center">
  <i>Made with ❤️ by EvoAI Team</i>
</p>
