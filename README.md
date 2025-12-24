# 🚀 Enterprise-Grade FastAPI Backend Template

<div align="center">

**A production-ready FastAPI backend template with clean architecture, built-in RBAC, and enterprise features - ready to use out of the box**

[English](README.en.md)

<!-- Star Area -->
<div align="center">
  <a href="https://github.com/JiayuXu0/FastAPI-Template" target="_blank">
    <img src="https://img.shields.io/badge/⭐_Give_a_Star-Support_Project-FFD700?style=for-the-badge&logo=github&logoColor=white&labelColor=FF6B6B&color=FFD700" alt="Give a Star">
  </a>
</div>

<!-- Interaction Prompt -->
<p align="center">
  ⭐ <strong>Like this project? Give it a star!</strong> ⭐
</p>

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/JiayuXu0/FastAPI-Template?style=social)](https://github.com/JiayuXu0/FastAPI-Template/stargazers)
[![Forks](https://img.shields.io/github/forks/JiayuXu0/FastAPI-Template?style=social)](https://github.com/JiayuXu0/FastAPI-Template/network/members)

[![UV](https://img.shields.io/badge/📦_Package_Manager-UV-blueviolet.svg)](https://github.com/astral-sh/uv)
[![Architecture](https://img.shields.io/badge/🏗️_Architecture-3_Layer-orange.svg)](#)
[![RBAC](https://img.shields.io/badge/🔐_Security-RBAC-red.svg)](#)
[![Docker](https://img.shields.io/badge/🐳_Docker-Ready-blue.svg)](https://www.docker.com/)

[📖 Quick Start](#-quick-start) • [🏗️ Architecture](#-architecture) • [📚 Development Guide](CLAUDE.md) • [🌐 Website](http://fastapi.infyai.cn/) • [🤝 Contributing](CONTRIBUTING.md) • [🌟 Give a Star!](https://github.com/JiayuXu0/FastAPI-Template)

</div>

---

## 📸 Project Preview

<div align="center">

### ✨ Core Features
<img src="docs/images/features-overview.svg" alt="Core Features" width="700">

### 🛠️ Tech Stack
<img src="docs/images/tech-stack.svg" alt="Tech Stack" width="700">

</div>

---

## 🌟 Why Choose This Template?

<div align="center">

| 🎯 **Enterprise Ready** | ⚡ **Developer Friendly** | 🛡️ **Secure by Default** | 📈 **High Performance** |
|:---:|:---:|:---:|:---:|
| Clean 3-layer architecture<br/>Production tested | 5-minute setup<br/>Zero configuration hassle | RBAC, JWT, Rate limiting<br/>Security best practices | Async/await throughout<br/>Redis caching built-in |

</div>

## ✨ Core Features

### 🔐 Authentication & Authorization
- **JWT Authentication** - Secure token authentication based on HS256 algorithm with refresh token mechanism
- **RBAC Permission Control** - Role-based access control with fine-grained API permissions
- **User Management** - Complete user registration, login, and permission assignment functionality
- **Role Management** - Flexible role definition and permission assignment

### 🗂️ Data Management
- **Menu Management** - Dynamic menu configuration with multi-level menu structure support
- **API Management** - Automated API permission configuration and management
- **Department Management** - Organizational structure management with hierarchical support
- **File Management** - Secure file upload, download, and storage functionality

### 🛡️ Security Protection
- **Login Rate Limiting** - Intelligent rate limiting based on slowapi to prevent brute force attacks (5 attempts/minute)
- **Token Refresh Rate Limiting** - Rate limiting protection for refresh token endpoints (10 attempts/minute)
- **Password Strength** - Enforced complex password policy (8+ characters with alphanumeric combination)
- **JWT Security** - 4-hour access token + 7-day refresh token mechanism with automatic token rotation
- **File Security** - File type validation, size limits, and malicious file detection
- **Security Headers** - Automatic XSS, CSRF, and clickjacking protection
- **CORS Configuration** - Strict cross-origin access control
- **Environment Validation** - Production environment configuration security checks
- **Audit Logging** - Complete user operation records and tracking

### 🏗️ Architecture Design
- **Three-Layer Architecture** - Clear separation: API → Service → Repository → Model
- **Async Support** - Fully asynchronous design for high-performance processing
- **Health Checks** - System status monitoring and version information endpoints
- **Database Migrations** - Versioned database management based on Aerich
- **Type Safety** - Complete Python type annotations

### ⚡ Performance Optimization
- **Connection Pool Optimization** - Database connection pool configuration for improved concurrency (20 connections + timeout control)
- **Caching System** - Redis integration with intelligent caching strategies and user cache management
- **Async Architecture** - Fully asynchronous design supporting high-concurrency access
- **Performance Monitoring** - Slow query alerts and performance metrics tracking

## 🛠️ Tech Stack

| Component | Technology | Version Requirement |
|-----------|------------|---------------------|
| **Language** | Python | 3.11+ |
| **Web Framework** | FastAPI | 0.100+ |
| **Database ORM** | Tortoise ORM | 0.20+ |
| **Database** | SQLite/PostgreSQL | - |
| **Authentication** | PyJWT | 2.8+ |
| **Data Validation** | Pydantic | 2.0+ |
| **Database Migration** | Aerich | 0.7+ |
| **Package Manager** | UV | latest |
| **Logging** | Loguru | 0.7+ |
| **Rate Limiting** | SlowAPI | 0.1.9+ |
| **Cache** | Redis | 4.5+ |

## 📁 Project Structure

```
evoai-backend-template/
├── src/                          # 📦 Source code directory
│   ├── api/v1/                   # 🌐 API routing layer (lightweight routes)
│   │   ├── users/               # 👥 User management API
│   │   ├── roles/               # 👑 Role management API
│   │   ├── menus/               # 📋 Menu management API
│   │   ├── files/               # 📁 File management API
│   │   └── ...
│   ├── services/                 # 🔧 Business logic layer (core business)
│   │   ├── base_service.py      # 🏗️ Service base class and permission service
│   │   ├── user_service.py      # 👤 User business logic
│   │   ├── file_service.py      # 📄 File business logic
│   │   └── ...
│   ├── repositories/             # 🗄️ Data access layer (CRUD operations)
│   ├── models/                   # 📊 Data model layer
│   │   ├── admin.py             # 👨‍💼 User role models
│   │   ├── base.py              # 🔷 Base model class
│   │   └── enums.py             # 📝 Enum definitions
│   ├── schemas/                  # ✅ Data validation layer
│   ├── core/                     # ⚙️ Core functionality
│   │   ├── dependency.py        # 🔗 Dependency injection
│   │   ├── middlewares.py       # 🛡️ Middlewares
│   │   └── init_app.py          # 🚀 Application initialization
│   ├── utils/                    # 🔧 Utility functions
│   └── settings/                 # ⚙️ Configuration management
├── migrations/                   # 📈 Database migration files
├── tests/                        # 🧪 Test files
├── uploads/                      # 📂 File upload directory
├── logs/                         # 📋 Log files
├── pyproject.toml               # 📦 UV project configuration
├── .env                         # 🔐 Environment variable configuration
└── CLAUDE.md                    # 🤖 Claude development guide
```

## 🚀 Quick Start

### ⚡ One-Click Project Creation (Recommended)

**🎉 New scaffolding tool `create-fastapi-app` has been released!**

<div align="center">

<a href="https://github.com/JiayuXu0/create-fastapi-app" target="_blank">
  <img src="https://img.shields.io/badge/🚀_create--fastapi--app-One-Click_Create_FastAPI_Project-00D8FF?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=009688&color=00D8FF" alt="create-fastapi-app">
</a>

<a href="https://github.com/JiayuXu0/create-fastapi-app" target="_blank">
  <img src="https://img.shields.io/badge/⭐_Star_Project-Support_Development-FFD700?style=for-the-badge&logo=github&logoColor=white&labelColor=FF6B6B&color=FFD700" alt="Star create-fastapi-app">
</a>

**⭐ If you find it useful, please give [create-fastapi-app](https://github.com/JiayuXu0/create-fastapi-app) a star! ⭐**

</div>

```bash
# 🚀 Using npx (Recommended)
npx create-fastapi-app@latest my-awesome-backend

# 🚀 Using npm
npm create fastapi-app@latest my-awesome-backend

# 🚀 Using yarn
yarn create fastapi-app my-awesome-backend

# 🚀 Using pnpm
pnpm create fastapi-app my-awesome-backend
```

**✨ Scaffolding Advantages:**
- 🎯 **Interactive Creation** - Friendly command-line interface with step-by-step configuration guidance
- 🔧 **Smart Configuration** - Automatically generates `.env` files and database configuration
- 📦 **Rich Templates** - Multiple options: basic, full, microservice versions, etc.
- 🚀 **Ready to Use** - Run immediately after generation with zero configuration
- 🛠️ **Tool Integration** - Pre-configured code checking, formatting, testing, and other development tools

> 💡 **Strongly recommend using the scaffolding tool! 10x faster than manual configuration!**
>
> 🔗 **Project URL**: https://github.com/JiayuXu0/create-fastapi-app
>
> ⭐ **Don't forget to give the scaffolding project a star! Your support is our motivation for continuous improvement!**

---

### 💻 Manual Installation (Traditional Method)

If you prefer manual configuration or need deep customization:

#### 1. Environment Setup

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the project
git clone <your-repo-url>
cd evoai-backend-template

# Install dependencies
uv sync
```

### 2. 🔐 Environment Configuration

**Copy environment configuration file:**
```bash
cp .env.example .env
```

**⚠️ Security configurations that must be modified:**

| Configuration Item | Description | Generation Method |
|-------------------|-------------|-------------------|
| `SECRET_KEY` | JWT signing key | `openssl rand -hex 32` |
| `SWAGGER_UI_PASSWORD` | API documentation access password | Set a strong password |
| `DB_PASSWORD` | Database password | Set a strong password |

**Configuration Example:**
```bash
# Basic configuration
SECRET_KEY=your_generated_secret_key_here
APP_TITLE=Your Project Name
PROJECT_NAME=YourProject

# Database configuration (SQLite recommended for development)
DB_ENGINE=sqlite
DB_PASSWORD=your_strong_password

# API documentation protection
SWAGGER_UI_USERNAME=admin
SWAGGER_UI_PASSWORD=your_strong_password

# CORS configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 3. Database Initialization

```bash
uv run aerich init-db
```

### 4. Start Service

```bash
# Development mode
uv run uvicorn src:app --reload --host 0.0.0.0 --port 8000

# Production mode
uv run uvicorn src:app --host 0.0.0.0 --port 8000 --workers 4
```

### 🐳 Run Project with Docker

```bash
# Build image (execute in project root directory)
docker build -t fastapi-template .

# Start container and map ports, optionally load environment variables
docker run --rm -p 8000:8000 --env-file .env fastapi-template
```

After the image starts, you can access http://localhost:8000/docs to verify the service is running, or use `curl http://localhost:8000/api/v1/base/health` for health check.

### 5. Access Service

- **🌐 Official Documentation**: http://fastapi.infyai.cn/
- **API Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/base/health
- **Version Information**: http://localhost:8000/api/v1/base/version
- **System Status**: Real-time system status monitoring

### 6. Default Account

```
Username: admin
Password: abcd1234
```

**🚨 Change password immediately after first login!**

---

## 📊 Project Statistics

<div align="center">

![GitHub repo size](https://img.shields.io/github/repo-size/JiayuXu0/FastAPI-Template)
![GitHub code size](https://img.shields.io/github/languages/code-size/JiayuXu0/FastAPI-Template)
![Lines of code](https://img.shields.io/tokei/lines/github/JiayuXu0/FastAPI-Template)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/JiayuXu0/FastAPI-Template)

</div>

## 🎉 Success Stories

> 💡 **Multiple teams have used this template to quickly build production-grade backend services**

- 🏢 **Enterprise Management System** - Permission management platform supporting 100,000+ users
- 🛒 **E-commerce Backend** - High-concurrency order processing system
- 📱 **Mobile App API** - Microservice architecture user center
- 🎯 **SaaS Platform** - Multi-tenant permission isolation system

**👥 If you're also using this template, [tell us](https://github.com/JiayuXu0/FastAPI-Template/discussions) your use case!**

## 🏗️ Architecture

### Three-Layer Architecture Pattern

```
┌─────────────────┐
│   API Layer     │  ← Route distribution, parameter validation
│  (api/v1/)      │
├─────────────────┤
│  Service Layer  │  ← Business logic, permission checks
│  (services/)    │
├─────────────────┤
│Repository Layer │  ← Database operations, CRUD
│ (repositories/) │
├─────────────────┤
│  Model Layer    │  ← Data model definitions
│   (models/)     │
└─────────────────┘
```

### Core Design Principles

1. **Single Responsibility** - Each layer only handles its own logic
2. **Dependency Injection** - Managed through FastAPI dependency system
3. **Type Safety** - Complete Python type annotations
4. **Async First** - Fully asynchronous design with high-concurrency support
5. **Security First** - Built-in multiple security protection mechanisms

## 📚 Development Guide

### Adding New Features

1. **Define Data Models** (`models/`)
2. **Create Data Schemas** (`schemas/`)
3. **Implement Repository** (`repositories/`)
4. **Write Service Business Logic** (`services/`)
5. **Add API Routes** (`api/v1/`)
6. **Generate Database Migrations** (`aerich migrate`)

For detailed steps, refer to the [CLAUDE.md](CLAUDE.md) development guide.

### 📖 Documentation System

This project integrates a powerful documentation system built on **MkDocs Material**, providing beautiful and feature-complete project documentation.

#### ✨ Documentation Features
- **🤖 Automatic API Documentation Generation** - Automatically extracts API information from FastAPI code
- **📝 Detailed Parameter Descriptions** - Includes request parameters, response formats, and usage examples
- **🎨 Material Design** - Modern UI design with dark mode support
- **🔍 Full-Text Search** - Quickly find documentation content
- **📱 Responsive Design** - Perfect mobile access support
- **🌐 Multi-Language Support** - English and Chinese documentation

#### 📂 Documentation Structure
```
docs/
├── index.md              # 📋 Project homepage
├── guide/                 # 🚀 Quick start guide
├── architecture/          # 🏗️ Architecture design documentation
├── api/                   # 📚 API interface documentation
│   ├── index.md          # API overview
│   ├── base.md           # Authentication & Authorization (auto-generated)
│   ├── users.md          # User Management (auto-generated)
│   ├── role.md           # Role Management (auto-generated)
│   └── ...               # Other API modules
├── changelog.md           # 📝 Changelog
├── faq.md                # ❓ FAQ
└── gen_pages.py          # 🔧 Documentation generation script
```

#### 🚀 Start Documentation Service
```bash
# Install documentation dependencies
uv sync --group docs

# Start development server (supports hot reload)
uv run mkdocs serve

# Build static documentation
uv run mkdocs build

# Deploy to GitHub Pages
uv run mkdocs gh-deploy
```

#### 🔄 Automatic API Documentation Generation
```bash
# Manually generate API documentation (usually automatic)
uv run python docs/gen_pages.py
```

#### 📋 API Documentation Contents
- **Complete Parameter Tables** - Parameter name, type, required, default value, description
- **Request Body Structure** - Pydantic model field details and JSON examples
- **Response Format Description** - Success/error response examples
- **Practical Code Examples** - cURL and Python requests usage examples
- **Authentication Requirements** - Bearer Token usage instructions

#### 🌐 Online Access
- **🌐 Official Documentation**: http://fastapi.infyai.cn/
- **Local Documentation**: http://localhost:8000 (mkdocs serve)
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

> 💡 **Tip**: API documentation automatically updates with code changes, ensuring documentation stays in sync with code!

### Database Operations

```bash
# Generate migration file
uv run aerich migrate --name "add_new_feature"

# Apply migrations
uv run aerich upgrade

# View migration history
uv run aerich history
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_users.py

# Generate coverage report
uv run pytest --cov=src --cov-report=html
```

## 🔒 Security Best Practices

### Production Environment Security Checks

#### ✅ Automatic Checks
- [x] **SECRET_KEY** Automatically generates secure key, at least 32 characters
- [x] **Password Strength** Enforced 8+ characters with alphanumeric combination
- [x] **Login Rate Limiting** Automatic brute force attack prevention
- [x] **JWT Security** 4-hour expiration + refresh mechanism
- [x] **Environment Validation** Automatic production environment configuration checks
- [x] **Error Protection** Hide technical details in production environment

#### 📋 Manual Checks
- [ ] **DEBUG Mode** Set `DEBUG=False` in production environment
- [ ] **Database** Use PostgreSQL instead of SQLite
- [ ] **CORS Configuration** Set specific domains, remove localhost
- [ ] **HTTPS** Enable HTTPS in production environment
- [ ] **Database Security** Use independent database account with limited permissions
- [ ] **Swagger Password** Set strong password to protect API documentation

### File Upload Security

- Whitelist validation for supported file types
- File size limits (default 500MB)
- Dangerous file type blacklist detection
- Secure filename generation mechanism
- Local file storage (extensible to cloud storage)

## 🔧 Configuration

### Environment Variables

| Variable Name | Required | Default Value | Description |
|--------------|----------|---------------|-------------|
| `SECRET_KEY` | ✅ | Auto-generated | JWT signing key (at least 32 characters) |
| `SWAGGER_UI_PASSWORD` | ✅ | - | API documentation access password (at least 8 characters) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | 240 | JWT access token expiration time (minutes) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | ❌ | 7 | JWT refresh token expiration time (days) |
| `APP_TITLE` | ❌ | Vue FastAPI Admin | Application title |
| `DB_ENGINE` | ❌ | postgres | Database type |
| `DB_HOST` | ❌ | localhost | Database host |
| `DB_PASSWORD` | ⚠️ | - | Database password (required in production) |
| `CORS_ORIGINS` | ❌ | localhost:3000 | Allowed CORS origins |
| `DEBUG` | ❌ | True | Debug mode |
| `APP_ENV` | ❌ | development | Application environment (development/production) |

### Database Support

- **SQLite** - Suitable for development and small deployments
- **PostgreSQL** - Recommended for production environments

## 📈 Performance Optimization

### 🚀 Implemented Optimizations
- **Async Processing** - Fully asynchronous architecture supporting high concurrency
- **Login Rate Limiting** - Brute force prevention, maximum 5 attempts per minute
- **Password Policy** - Enforced complex passwords to enhance account security
- **JWT Optimization** - 4-hour short-term token + refresh mechanism
- **Error Protection** - Hide technical details in production environment
- **Health Monitoring** - System status and version information endpoints

### 🔄 Planned Optimizations
- **Performance Monitoring** - Slow query alerts and metrics tracking
- **Middleware** - Request compression, cache header settings
- **GraphQL** - GraphQL interface support
- **WebSocket** - Real-time communication functionality

## 🤝 Contributing

1. Fork the project repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

### Code Standards

#### 🔧 Pre-commit Hooks (Recommended)
```bash
# Hooks are automatically installed during uv sync
# Automatically runs code checks and formatting on each git commit

# Manually run all checks
uv run pre-commit run --all-files

# Disable hooks if you don't want to use them
uv run pre-commit uninstall

# Skip single check (emergency situations)
git commit --no-verify -m "urgent fix"
```

#### 📋 Coding Standards
- Follow **PEP 8** coding standards
- Use **Google-style** docstrings
- Add **type annotations** to all functions
- Write **unit tests** covering key functionality
- Use **ruff** for code checking and formatting

📖 **Detailed Instructions**: See [Pre-commit Hooks Guide](docs/pre-commit-guide.md)

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🔗 Related Links

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [Tortoise ORM Documentation](https://tortoise.github.io/)
- [UV Package Manager](https://github.com/astral-sh/uv)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)

---

## 🆘 Get Help

If you encounter any issues while using this project:

1. 📖 Check [CLAUDE.md](CLAUDE.md) for detailed development guide
2. 🔍 Check [Issues](../../issues) for similar problems
3. 💬 Create a new [Issue](../../issues/new) to describe the problem
4. 📧 Contact the maintainers

**Ready to use, professional and reliable enterprise-grade FastAPI backend template** 🚀

## 📝 Changelog

### 🆕 v1.2.0 - Performance and Security Dual Upgrade (2025-07-14)

#### ⚡ Performance Optimization
- ✅ **Database Connection Pool Optimization** - 20 connection pool + timeout control, improved concurrency performance
- ✅ **Redis Cache Integration** - Intelligent caching strategy, user data cache management
- ✅ **Cache Decorator** - Elegant caching solution with configurable TTL
- ✅ **User Cache Management** - Automatic cache cleanup mechanism

#### 🔐 JWT Security Enhancement
- ✅ **Refresh Token Mechanism** - 7-day refresh token + automatic rotation strategy
- ✅ **Dual Token System** - Access token (4 hours) + Refresh token (7 days)
- ✅ **Token Type Validation** - Prevents incorrect token type usage
- ✅ **Refresh Endpoint Rate Limiting** - 10 attempts/minute refresh protection

#### 🏥 Monitoring Features
- ✅ **Health Check Endpoint** - `/api/v1/base/health`
- ✅ **Version Information Endpoint** - `/api/v1/base/version`
- ✅ **System Status Monitoring** - Real-time service status display

#### 🛠️ Developer Experience
- ✅ **Automatic SECRET_KEY Generation** - No manual configuration needed
- ✅ **Detailed Error Messages** - Developer-friendly error information
- ✅ **Enhanced Configuration Validation** - Automatic configuration checks on startup

### 📋 v1.0.0 - Base Version
- 🏗️ Three-layer architecture design
- 🔐 RBAC permission management
- 📊 Complete CRUD operations
- 🗄️ Database migration support

---

## 🏆 Highlights

<div align="center">

<!-- Achievement Display -->
<div align="center">

### 🎯 Developer Recognition

| ⭐ **Stars** | 🍴 **Forks** | 👥 **Users** |
|:---:|:---:|:---:|
| Growing | Active Usage | Enterprise-Grade |

</div>

### 🚀 Quick Start

**🎯 Method 1: Scaffold Creation (Recommended)**
```bash
npx create-fastapi-app@latest my-project
cd my-project && uv run uvicorn src:app --reload
# 🎉 Start a complete enterprise-grade backend service in 2 minutes!
```

**⭐ Don't forget to star the scaffold: https://github.com/JiayuXu0/create-fastapi-app**

**📦 Method 2: Template Clone**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/JiayuXu0/FastAPI-Template.git
cd FastAPI-Template && uv sync && cp .env.example .env
uv run aerich init-db && uv run uvicorn src:app --reload
# 🎉 Start a complete enterprise-grade backend service in 5 minutes!
```

### 💎 Tech Stack Comparison

| Traditional Approach ❌ | This Template ✅ |
|:---:|:---:|
| Complex environment configuration | UV one-click dependency management |
| Messy project structure | Clear three-layer architecture |
| Manual permission management | Complete RBAC system |
| Lack of security protection | Multiple security mechanisms |
| Incomplete documentation | Detailed development guide |

</div>

## 🌟 Community Support

<div align="center">

**Join our developer community and build a better backend template together!**

<!-- Star Call -->
<div align="center">

### 🚀 Support Project Development

#### ⭐ Give the Template Project a Star
If this template helps you, please give us a star⭐

<a href="https://github.com/JiayuXu0/FastAPI-Template" target="_blank">
  <img src="https://img.shields.io/badge/⭐_Star_Now-Support_Template-FFD700?style=for-the-badge&logo=github&logoColor=white&labelColor=FF6B6B&color=FFD700" alt="Star Template">
</a>

#### 🚀 Don't Forget create-fastapi-app Scaffold
**More importantly, also give our scaffolding tool a star!**

<a href="https://github.com/JiayuXu0/create-fastapi-app" target="_blank">
  <img src="https://img.shields.io/badge/⭐_Star_Scaffold-create--fastapi--app-00D8FF?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=009688&color=00D8FF" alt="Star Scaffold">
</a>

**🎯 Why Star the Scaffold Project?**
- 🚀 Let more developers discover this convenient tool
- 💪 Motivate us to continuously improve and add new features
- 🌟 Your support is the driving force for open source project development

</div>

[![GitHub Discussions](https://img.shields.io/github/discussions/JiayuXu0/FastAPI-Template?color=blue&logo=github)](https://github.com/JiayuXu0/FastAPI-Template/discussions)
[![GitHub Issues](https://img.shields.io/github/issues/JiayuXu0/FastAPI-Template?color=green&logo=github)](https://github.com/JiayuXu0/FastAPI-Template/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/JiayuXu0/FastAPI-Template?color=orange&logo=github)](https://github.com/JiayuXu0/FastAPI-Template/pulls)

[💬 Discussions](https://github.com/JiayuXu0/FastAPI-Template/discussions) • [🐛 Report Issues](https://github.com/JiayuXu0/FastAPI-Template/issues) • [🔀 Submit PR](https://github.com/JiayuXu0/FastAPI-Template/pulls)

</div>

## 🎯 Roadmap

- [x] ✅ **v1.0** - Base three-layer architecture and RBAC system
- [x] ✅ **v1.1** - UV package manager integration
- [x] ✅ **v1.2** - Database connection pool optimization + Redis cache + JWT refresh mechanism
- [ ] 🚧 **v1.3** - GraphQL API support
- [ ] 📅 **v1.4** - Microservice architecture expansion
- [ ] 📅 **v1.5** - Real-time communication (WebSocket)
- [ ] 📅 **v2.0** - Cloud-native deployment solution

[View Full Roadmap →](https://github.com/JiayuXu0/FastAPI-Template/projects)

---
