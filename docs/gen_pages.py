#!/usr/bin/env python3
"""
API documentation auto-generation script
Extracts route information from FastAPI application and generates API documentation
"""

import inspect
import json
import sys
from pathlib import Path
from typing import Any, Union

import mkdocs_gen_files

# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from fastapi import FastAPI
    from fastapi.openapi.utils import get_openapi
    from fastapi.routing import APIRoute
    from pydantic import BaseModel

    # Import application
    from src import app
except ImportError as e:
    print(f"Unable to import FastAPI application: {e}")
    app = None


def get_model_fields(model: type[BaseModel]) -> list[dict[str, Any]]:
    """提取Pydantic模型的字段信息"""
    fields = []
    if not hasattr(model, "model_fields"):
        return fields

    for field_name, field_info in model.model_fields.items():
        field_type = field_info.annotation
        field_type_str = str(field_type).replace("typing.", "").replace("builtins.", "")

        # 获取字段描述
        description = ""
        if hasattr(field_info, "description") and field_info.description:
            description = field_info.description
        elif hasattr(field_info, "title") and field_info.title:
            description = field_info.title

        # 获取默认值
        default = None
        if hasattr(field_info, "default") and field_info.default is not None:
            default = field_info.default

        # 获取示例值
        example = None
        if hasattr(field_info, "examples") and field_info.examples:
            example = (
                field_info.examples[0]
                if isinstance(field_info.examples, list)
                else field_info.examples
            )
        elif hasattr(field_info, "example") and field_info.example is not None:
            example = field_info.example

        # 获取约束
        constraints = []
        if hasattr(field_info, "min_length") and field_info.min_length is not None:
            constraints.append(f"Min length: {field_info.min_length}")
        if hasattr(field_info, "max_length") and field_info.max_length is not None:
            constraints.append(f"Max length: {field_info.max_length}")
        if hasattr(field_info, "ge") and field_info.ge is not None:
            constraints.append(f"Min value: {field_info.ge}")
        if hasattr(field_info, "le") and field_info.le is not None:
            constraints.append(f"Max value: {field_info.le}")
        if hasattr(field_info, "pattern") and field_info.pattern is not None:
            constraints.append(f"Pattern: `{field_info.pattern}`")

        required = (
            field_info.is_required() if hasattr(field_info, "is_required") else True
        )

        fields.append(
            {
                "name": field_name,
                "type": field_type_str,
                "required": required,
                "description": description,
                "default": default,
                "example": example,
                "constraints": constraints,
            }
        )

    return fields


def extract_route_details(route: APIRoute) -> dict[str, Any]:
    """Extract detailed route information, including parameters and responses"""
    route_info = {
        "path": route.path,
        "methods": list(route.methods),
        "name": route.name,
        "summary": getattr(route, "summary", ""),
        "description": getattr(route, "description", ""),
        "tags": getattr(route, "tags", []),
        "deprecated": getattr(route, "deprecated", False),
        "parameters": [],
        "request_body": None,
        "responses": {},
    }

    # Get endpoint function
    endpoint = route.endpoint
    if endpoint:
        # Get function signature
        sig = inspect.signature(endpoint)

        # Analyze parameters
        for param_name, param in sig.parameters.items():
            if param_name in ["request", "response", "background_tasks"]:
                continue

            param_info = {
                "name": param_name,
                "in": "query",  # Default
                "type": "string",  # Default
                "required": param.default == param.empty,
                "description": "",
                "default": None if param.default == param.empty else param.default,
            }

            # Check parameter annotations
            if param.annotation != param.empty:
                # Handle Query, Body, Path parameters
                if hasattr(param.default, "__class__"):
                    param_class = param.default.__class__.__name__

                    if param_class == "Query" or "Query" in str(param.default):
                        param_info["in"] = "query"
                        if hasattr(param.default, "description"):
                            param_info["description"] = param.default.description
                        if hasattr(param.default, "default"):
                            param_info["default"] = param.default.default
                            param_info["required"] = param.default.default == ...

                    elif param_class == "Body" or "Body" in str(param.default):
                        param_info["in"] = "body"
                        if hasattr(param.default, "description"):
                            param_info["description"] = param.default.description

                    elif param_class == "Path" or "Path" in str(param.default):
                        param_info["in"] = "path"
                        if hasattr(param.default, "description"):
                            param_info["description"] = param.default.description

                # Handle Pydantic models - this is a key fix
                try:
                    if inspect.isclass(param.annotation) and issubclass(
                        param.annotation, BaseModel
                    ):
                        param_info["in"] = "body"
                        param_info["type"] = param.annotation.__name__
                        param_info["model_fields"] = get_model_fields(param.annotation)
                        route_info["request_body"] = param_info
                        continue
                except (TypeError, AttributeError):
                    # If not a class or not a subclass of BaseModel, continue with other processing
                    pass

                # Handle generics and Union types
                if hasattr(param.annotation, "__origin__"):
                    if param.annotation.__origin__ is Union:
                        # Handle Union types, e.g., Optional[str]
                        args = param.annotation.__args__
                        if len(args) == 2 and type(None) in args:
                            # This is an Optional type
                            param_info["required"] = False
                            non_none_type = (
                                args[0] if args[1] is type(None) else args[1]
                            )
                            param_info["type"] = (
                                str(non_none_type)
                                .replace("typing.", "")
                                .replace("builtins.", "")
                            )
                        else:
                            param_info["type"] = (
                                str(param.annotation)
                                .replace("typing.", "")
                                .replace("builtins.", "")
                            )
                    else:
                        param_info["type"] = (
                            str(param.annotation)
                            .replace("typing.", "")
                            .replace("builtins.", "")
                        )
                else:
                    # Simplify type name
                    param_info["type"] = (
                        str(param.annotation)
                        .replace("typing.", "")
                        .replace("builtins.", "")
                    )

            if param_info["in"] != "body":
                route_info["parameters"].append(param_info)

        # Get response model
        if hasattr(route, "response_model") and route.response_model:
            response_model = route.response_model
            try:
                if inspect.isclass(response_model) and issubclass(
                    response_model, BaseModel
                ):
                    route_info["responses"]["200"] = {
                        "model": response_model.__name__,
                        "fields": get_model_fields(response_model),
                    }
            except (TypeError, AttributeError):
                pass

    return route_info


def generate_parameter_table(parameters: list[dict[str, Any]]) -> str:
    """Generate parameter table"""
    if not parameters:
        return "No parameters required"

    table = "| Parameter Name | Type | Location | Required | Description | Default Value |\n"
    table += "|----------------|------|----------|----------|-------------|---------------|\n"

    for param in parameters:
        required = "Yes" if param.get("required", False) else "No"
        default = param.get("default", "-")
        if default is None:
            default = "null"
        elif default == ...:
            default = "-"

        table += f"| {param['name']} | `{param['type']}` | {param['in']} | {required} | {param.get('description', '')} | {default} |\n"

    return table


def generate_request_body_section(request_body: dict[str, Any]) -> str:
    """Generate request body documentation"""
    if not request_body:
        return ""

    content = "### Request Body\n\n"
    content += "**Content-Type**: `application/json`\n\n"

    if "model_fields" in request_body:
        content += f"**Model**: `{request_body['type']}`\n\n"

        # Generate field table
        content += "| Field Name | Type | Required | Description | Example | Constraints |\n"
        content += "|------------|------|----------|-------------|---------|-------------|\n"

        for field in request_body["model_fields"]:
            required = "Yes" if field["required"] else "No"
            example = field.get("example", "")
            if example:
                example = f"`{example}`"
            constraints = "<br>".join(field.get("constraints", []))

            content += f"| {field['name']} | `{field['type']}` | {required} | {field.get('description', '')} | {example} | {constraints} |\n"

        # Generate example
        content += "\n**Request Example**:\n\n```json\n"
        example_data = {}
        for field in request_body["model_fields"]:
            if field.get("example") is not None:
                example_data[field["name"]] = field["example"]
            elif field["required"]:
                # Generate more realistic examples based on field name and type
                field_name = field["name"].lower()
                field_type = field["type"].lower()

                if "email" in field_name:
                    example_data[field["name"]] = "admin@example.com"
                elif "username" in field_name or "name" == field_name:
                    example_data[field["name"]] = "admin"
                elif "password" in field_name:
                    example_data[field["name"]] = "password123"
                elif "id" in field_name and "int" in field_type:
                    example_data[field["name"]] = 1
                elif "bool" in field_type:
                    example_data[field["name"]] = True
                elif "list" in field_type:
                    if "role" in field_name:
                        example_data[field["name"]] = [1, 2]
                    else:
                        example_data[field["name"]] = []
                elif "str" in field_type:
                    if "desc" in field_name or "description" in field_name:
                        example_data[field["name"]] = "Description information"
                    elif "path" in field_name:
                        example_data[field["name"]] = "/api/v1/example"
                    elif "method" in field_name:
                        example_data[field["name"]] = "GET"
                    elif "tag" in field_name:
                        example_data[field["name"]] = "Example Module"
                    else:
                        example_data[field["name"]] = "Example text"
                elif "int" in field_type:
                    example_data[field["name"]] = 1
                else:
                    example_data[field["name"]] = None

        content += json.dumps(example_data, indent=2, ensure_ascii=False)
        content += "\n```\n\n"

    return content


def generate_module_doc(module_name: str, routes: list[dict[str, Any]]) -> str:
    """Generate documentation for module"""

    # Module name mapping
    module_names = {
        "users": "User Management",
        "role": "Role Management",
        "menu": "Menu Management",
        "files": "File Management",
        "dept": "Department Management",
        "api": "API Permissions",
        "auditlog": "Audit Log",
        "base": "Authentication & Authorization",
    }

    module_display_name = module_names.get(module_name, module_name.title())

    content = f"""# {module_display_name} API

## Overview

API interface documentation for {module_display_name}.

"""

    # Generate detailed documentation for each route
    for route_data in routes:
        # Extract detailed information
        route_details = (
            extract_route_details(route_data)
            if isinstance(route_data, APIRoute)
            else route_data
        )

        content += f"## {route_details['summary'] or route_details['name']}\n\n"

        # Basic information
        content += f"- **Path**: `{route_details['path']}`\n"
        content += f"- **Method**: {', '.join(f'`{method}`' for method in route_details['methods'])}\n"

        if route_details["tags"]:
            content += f"- **Tags**: {', '.join(route_details['tags'])}\n"

        if route_details.get("deprecated"):
            content += "- **Status**: ⚠️ Deprecated\n"

        content += "\n"

        # Description
        if route_details["description"]:
            content += f"### Description\n\n{route_details['description']}\n\n"

        # Parameters
        if route_details.get("parameters"):
            content += "### Request Parameters\n\n"
            content += generate_parameter_table(route_details["parameters"])
            content += "\n"

        # Request body
        if route_details.get("request_body"):
            content += generate_request_body_section(route_details["request_body"])

        # Response
        content += "### Response\n\n"
        content += "**Success Response**:\n\n"
        content += "- **Status Code**: `200`\n"
        content += "- **Content-Type**: `application/json`\n\n"

        # Standard response format
        content += "```json\n{\n"
        content += '  "code": 200,\n'
        content += '  "msg": "success",\n'
        content += '  "data": ...\n'
        content += "}\n```\n\n"

        # Error response
        content += "**Error Response**:\n\n"
        content += "- **Status Code**: `400` / `401` / `403` / `404` / `500`\n\n"
        content += "```json\n{\n"
        content += '  "code": 400,\n'
        content += '  "msg": "Error message",\n'
        content += '  "data": null\n'
        content += "}\n```\n\n"

        # Usage examples
        content += "### Usage Examples\n\n"

        # cURL example
        content += "**cURL**:\n```bash\n"

        method = (
            list(route_details["methods"])[0] if route_details["methods"] else "GET"
        )

        # Build cURL command
        curl_cmd = f'curl -X {method} "http://localhost:8000{route_details["path"]}'

        # Add query parameter examples
        query_params = [
            p for p in route_details.get("parameters", []) if p["in"] == "query"
        ]
        if query_params:
            param_examples = []
            for param in query_params:
                if param.get("example"):
                    param_examples.append(f"{param['name']}={param['example']}")
                elif param["required"]:
                    param_examples.append(f"{param['name']}=...")

            if param_examples:
                curl_cmd += "?" + "&".join(param_examples)

        curl_cmd += '"'

        # Add authentication header
        if module_name != "base":
            curl_cmd += ' \\\n  -H "Authorization: Bearer <your-token>"'

        # Add request body
        if method in ["POST", "PUT", "PATCH"] and route_details.get("request_body"):
            curl_cmd += ' \\\n  -H "Content-Type: application/json"'
            if route_details["request_body"].get("model_fields"):
                example_data = {}
                for field in route_details["request_body"]["model_fields"]:
                    if field.get("example") is not None:
                        example_data[field["name"]] = field["example"]
                    elif field["required"]:
                        # Generate more realistic examples based on field name and type
                        field_name = field["name"].lower()
                        field_type = field["type"].lower()

                        if "email" in field_name:
                            example_data[field["name"]] = "admin@example.com"
                        elif "username" in field_name or "name" == field_name:
                            example_data[field["name"]] = "admin"
                        elif "password" in field_name:
                            example_data[field["name"]] = "password123"
                        elif "id" in field_name and "int" in field_type:
                            example_data[field["name"]] = 1
                        elif "bool" in field_type:
                            example_data[field["name"]] = True
                        elif "list" in field_type:
                            if "role" in field_name:
                                example_data[field["name"]] = [1, 2]
                            else:
                                example_data[field["name"]] = []
                        elif "str" in field_type:
                            if "desc" in field_name or "description" in field_name:
                                example_data[field["name"]] = "Description information"
                            elif "path" in field_name:
                                example_data[field["name"]] = "/api/v1/example"
                            elif "method" in field_name:
                                example_data[field["name"]] = "GET"
                            elif "tag" in field_name:
                                example_data[field["name"]] = "Example Module"
                            else:
                                example_data[field["name"]] = "Example text"
                        else:
                            example_data[field["name"]] = "value"

                if example_data:
                    curl_cmd += (
                        f" \\\n  -d '{json.dumps(example_data, ensure_ascii=False)}'"
                    )
                else:
                    curl_cmd += ' \\\n  -d \'{"key": "value"}\''

        content += curl_cmd + "\n```\n\n"

        # Python example
        content += "**Python (requests)**:\n```python\n"
        content += "import requests\n\n"

        if module_name != "base":
            content += "headers = {\n"
            content += '    "Authorization": "Bearer <your-token>"\n'
            content += "}\n\n"

        if method == "GET":
            if query_params:
                content += "params = {\n"
                for param in query_params[:3]:  # Only show first 3 parameters as example
                    if param.get("example"):
                        content += f'    "{param["name"]}": "{param["example"]}",\n'
                    elif param["required"]:
                        content += f'    "{param["name"]}": "...",\n'
                content += "}\n\n"
                content += "response = requests.get(\n"
                content += f'    "http://localhost:8000{route_details["path"]}",\n'
                if module_name != "base":
                    content += "    headers=headers,\n"
                content += "    params=params\n"
                content += ")\n"
            else:
                content += "response = requests.get(\n"
                content += f'    "http://localhost:8000{route_details["path"]}"'
                if module_name != "base":
                    content += ",\n    headers=headers"
                content += "\n)\n"

        elif method in ["POST", "PUT", "PATCH"]:
            if route_details.get("request_body") and route_details["request_body"].get(
                "model_fields"
            ):
                content += "data = {\n"
                example_count = 0
                for field in route_details["request_body"]["model_fields"]:
                    if example_count >= 5:  # Limit display count
                        break

                    if field.get("example") is not None:
                        if isinstance(field["example"], str):
                            content += f'    "{field["name"]}": "{field["example"]}",\n'
                        else:
                            content += f'    "{field["name"]}": {json.dumps(field["example"])},\n'
                        example_count += 1
                    elif field["required"]:
                        # Generate realistic example data
                        field_name = field["name"].lower()
                        field_type = field["type"].lower()

                        if "email" in field_name:
                            content += f'    "{field["name"]}": "admin@example.com",\n'
                        elif "username" in field_name or "name" == field_name:
                            content += f'    "{field["name"]}": "admin",\n'
                        elif "password" in field_name:
                            content += f'    "{field["name"]}": "password123",\n'
                        elif "id" in field_name and "int" in field_type:
                            content += f'    "{field["name"]}": 1,\n'
                        elif "bool" in field_type:
                            content += f'    "{field["name"]}": True,\n'
                        elif "list" in field_type:
                            if "role" in field_name:
                                content += f'    "{field["name"]}": [1, 2],\n'
                            else:
                                content += f'    "{field["name"]}": [],\n'
                        elif "str" in field_type:
                            if "desc" in field_name or "description" in field_name:
                                content += f'    "{field["name"]}": "Description information",\n'
                            elif "path" in field_name:
                                content += (
                                    f'    "{field["name"]}": "/api/v1/example",\n'
                                )
                            elif "method" in field_name:
                                content += f'    "{field["name"]}": "GET",\n'
                            elif "tag" in field_name:
                                content += f'    "{field["name"]}": "Example Module",\n'
                            else:
                                content += f'    "{field["name"]}": "Example text",\n'
                        else:
                            content += f'    "{field["name"]}": "value",\n'
                        example_count += 1
                content += "}\n\n"

            content += f"response = requests.{method.lower()}(\n"
            content += f'    "http://localhost:8000{route_details["path"]}",\n'
            if module_name != "base":
                content += "    headers=headers,\n"
            if route_details.get("request_body"):
                content += "    json=data\n"
            content += ")\n"

        elif method == "DELETE":
            content += "response = requests.delete(\n"
            content += f'    "http://localhost:8000{route_details["path"]}"'
            if module_name != "base":
                content += ",\n    headers=headers"
            content += "\n)\n"

        content += "\nprint(response.json())\n"
        content += "```\n\n"

        # 添加分隔线
        content += "---\n\n"

    return content


def extract_route_info(app: FastAPI) -> dict[str, list[Any]]:
    """提取路由信息，返回原始的APIRoute对象"""
    if app is None:
        return {}

    routes_info = {}

    for route in app.routes:
        if isinstance(route, APIRoute):
            # 提取路径的模块信息
            path_parts = route.path.split("/")
            if (
                len(path_parts) >= 4
                and path_parts[1] == "api"
                and path_parts[2] == "v1"
            ):
                module = path_parts[3]

                if module not in routes_info:
                    routes_info[module] = []

                # 直接保存APIRoute对象
                routes_info[module].append(route)

    return routes_info


def generate_api_index() -> str:
    """Generate API index page"""
    return """# API Documentation

## Overview

This is the complete API documentation for the FastAPI backend template. All APIs follow RESTful design principles and use JSON format for data exchange.

## Authentication

Most APIs require JWT authentication. Please first obtain an access token through the login endpoint, then include it in the request header:

```
Authorization: Bearer <your-access-token>
```

## Response Format

All API responses follow a unified format:

### Success Response
```json
{
  "code": 200,
  "msg": "success",
  "data": {...}
}
```

### Error Response
```json
{
  "code": 400,
  "msg": "error message",
  "data": null
}
```

### Error Code Description

| Error Code | Description |
|------------|-------------|
| 200 | Success |
| 400 | Request parameter error |
| 401 | Unauthenticated |
| 403 | No permission |
| 404 | Resource does not exist |
| 422 | Parameter validation failed |
| 429 | Request too frequent |
| 500 | Internal server error |

## API Modules

- [Authentication & Authorization](base.md) - User login, token refresh, etc.
- [User Management](users.md) - User CRUD operations
- [Role Management](role.md) - Role permission management
- [Menu Management](menu.md) - System menu configuration
- [File Management](files.md) - File upload and download
- [Department Management](dept.md) - Organizational structure management
- [API Permissions](api.md) - API permission control
- [Audit Log](auditlog.md) - Operation log records

## Online Testing

After starting the service, you can access the interactive API documentation at the following addresses:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Request Limits

- File upload size limit: 10MB
- Login attempt limit: 5 times/minute
- Token refresh limit: 10 times/minute
- API request frequency: Depends on specific endpoint

## Health Check

- **Health Status**: `GET /api/v1/base/health`
- **Version Information**: `GET /api/v1/base/version`
"""


def main():
    """Main function"""
    print("Generating API documentation...")

    # Generate API index page
    with mkdocs_gen_files.open("api/index.md", "w") as f:
        f.write(generate_api_index())

    # If application is available, generate detailed documentation
    if app is not None:
        try:
            # Extract route information
            routes_info = extract_route_info(app)

            # Generate documentation for each module
            for module_name, routes in routes_info.items():
                file_name = f"api/{module_name}.md"
                content = generate_module_doc(module_name, routes)

                with mkdocs_gen_files.open(file_name, "w") as f:
                    f.write(content)

                print(f"Generated: {file_name}")

            # Generate OpenAPI specification file
            openapi_schema = get_openapi_schema(app)
            if openapi_schema:
                with mkdocs_gen_files.open("api/openapi.json", "w") as f:
                    json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
                print("Generated: api/openapi.json")

            print(f"API documentation generation complete! Generated {len(routes_info)} module documents")

        except Exception as e:
            print(f"Error generating API documentation: {e}")
            import traceback

            traceback.print_exc()
            print("Will generate basic documentation structure...")

            # Generate basic documentation structure
            basic_modules = [
                "base",
                "users",
                "role",
                "menu",
                "files",
                "dept",
                "api",
                "auditlog",
            ]

            for module in basic_modules:
                file_name = f"api/{module}.md"
                content = f"""# {module.title()} API

## Overview

API interface documentation for {module.title()}.

!!! note "Note"
    Please start the FastAPI application and regenerate the documentation to get complete API information.

## Quick Start

```bash
# Start application
uv run uvicorn src:app --reload

# Access interactive documentation
open http://localhost:8000/docs
```
"""

                with mkdocs_gen_files.open(file_name, "w") as f:
                    f.write(content)

                print(f"Generated basic documentation: {file_name}")

    else:
        print("FastAPI application not available, generating basic documentation structure...")

        # Generate basic documentation structure
        basic_modules = [
            "base",
            "users",
            "role",
            "menu",
            "files",
            "dept",
            "api",
            "auditlog",
        ]

        for module in basic_modules:
            file_name = f"api/{module}.md"
            content = f"""# {module.title()} API

## Overview

API interface documentation for {module.title()}.

!!! note "Note"
    Please start the FastAPI application and regenerate the documentation to get complete API information.

## Quick Start

```bash
# Start application
uv run uvicorn src:app --reload

# Access interactive documentation
open http://localhost:8000/docs
```
"""

            with mkdocs_gen_files.open(file_name, "w") as f:
                f.write(content)

            print(f"Generated basic documentation: {file_name}")


def get_openapi_schema(app: FastAPI) -> dict:
    """获取OpenAPI模式"""
    if app is None:
        return {}

    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )


if __name__ == "__main__":
    main()
