"""Architecture level boundary and dependency direction assertion tests."""

import ast
from pathlib import Path


def _get_python_files(package_dir: Path) -> list[Path]:
    """Retrieve all Python source files in a package directory."""
    if not package_dir.exists():
        return []
    return [p for p in package_dir.rglob("*.py") if p.is_file()]


def _extract_imported_modules(file_path: Path) -> list[str]:
    """Extract top-level imported module names from a Python source file using AST."""
    content = file_path.read_text(encoding="utf-8")
    tree = ast.parse(content, filename=str(file_path))
    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports


def test_domain_framework_independence() -> None:
    """Verify that domain layer contains zero framework or infrastructure imports."""
    domain_dir = Path(__file__).parent.parent.parent / "app" / "domain"
    domain_files = _get_python_files(domain_dir)

    forbidden_patterns = [
        "fastapi",
        "starlette",
        "httpx",
        "sqlalchemy",
        "redis",
        "app.infrastructure",
        "app.api",
    ]

    for py_file in domain_files:
        imports = _extract_imported_modules(py_file)
        for imp in imports:
            for forbidden in forbidden_patterns:
                assert not imp.startswith(forbidden), (
                    f"Forbidden import '{imp}' found in domain file {py_file.name}"
                )


def test_application_http_independence() -> None:
    """Verify that application layer contains zero HTTP framework or API layer imports."""
    app_layer_dir = Path(__file__).parent.parent.parent / "app" / "application"
    app_files = _get_python_files(app_layer_dir)

    forbidden_patterns = [
        "fastapi",
        "starlette",
        "httpx",
        "app.api",
    ]

    for py_file in app_files:
        imports = _extract_imported_modules(py_file)
        for imp in imports:
            for forbidden in forbidden_patterns:
                assert not imp.startswith(forbidden), (
                    f"Forbidden import '{imp}' found in application file {py_file.name}"
                )


def test_core_isolation() -> None:
    """Verify that core layer does not depend on higher-level feature layers."""
    core_dir = Path(__file__).parent.parent.parent / "app" / "core"
    core_files = _get_python_files(core_dir)

    forbidden_patterns = [
        "app.api",
        "app.application",
        "app.domain",
        "app.infrastructure",
    ]

    for py_file in core_files:
        imports = _extract_imported_modules(py_file)
        for imp in imports:
            for forbidden in forbidden_patterns:
                assert not imp.startswith(forbidden), (
                    f"Forbidden import '{imp}' found in core file {py_file.name}"
                )


def test_schemas_isolation() -> None:
    """Verify that schemas layer does not import API or infrastructure modules."""
    schemas_dir = Path(__file__).parent.parent.parent / "app" / "schemas"
    schemas_files = _get_python_files(schemas_dir)

    forbidden_patterns = [
        "app.api",
        "app.infrastructure",
    ]

    for py_file in schemas_files:
        imports = _extract_imported_modules(py_file)
        for imp in imports:
            for forbidden in forbidden_patterns:
                assert not imp.startswith(forbidden), (
                    f"Forbidden import '{imp}' found in schema file {py_file.name}"
                )


def test_no_utils_dumping_ground() -> None:
    """Enforce utils policy: app/utils directory must not exist."""
    utils_dir = Path(__file__).parent.parent.parent / "app" / "utils"
    msg = "Anti-pattern detected: app/utils dumping ground directory exists."
    assert not utils_dir.exists(), msg


def test_domain_environment_isolation() -> None:
    """Verify domain layer has zero environment variable or secret access."""
    domain_dir = Path(__file__).parent.parent.parent / "app" / "domain"
    domain_files = _get_python_files(domain_dir)

    forbidden_tokens = [
        "os.environ",
        "os.getenv",
        "dotenv",
        "get_settings",
        "SecretStr",
        "SECRET_KEY",
        "DATABASE_URL",
        "REDIS_URL",
        "secret_manager",
    ]

    for py_file in domain_files:
        content = py_file.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in content, (
                f"Forbidden environment/secret access '{token}' found in domain file {py_file.name}"
            )


def test_domain_logging_isolation() -> None:
    """Verify domain layer has zero direct imports of infrastructure logging modules."""
    domain_dir = Path(__file__).parent.parent.parent / "app" / "domain"
    domain_files = _get_python_files(domain_dir)

    forbidden_patterns = ["app.core.logging", "logging.config"]

    for py_file in domain_files:
        imports = _extract_imported_modules(py_file)
        for imp in imports:
            for forbidden in forbidden_patterns:
                assert not imp.startswith(forbidden), (
                    f"Forbidden logging import '{imp}' found in domain file {py_file.name}"
                )


def test_exception_layer_http_isolation() -> None:
    """Verify exception definitions in domain, application, and infrastructure remain decoupled."""

    app_root = Path(__file__).parent.parent.parent / "app"
    layers_to_check = [
        app_root / "domain" / "exceptions",
        app_root / "application" / "exceptions",
        app_root / "infrastructure" / "exceptions",
    ]

    forbidden_patterns = ["fastapi", "starlette", "httpx"]

    for layer_dir in layers_to_check:
        py_files = _get_python_files(layer_dir)
        for py_file in py_files:
            imports = _extract_imported_modules(py_file)
            for imp in imports:
                for forbidden in forbidden_patterns:
                    assert not imp.startswith(forbidden), (
                        f"Forbidden HTTP import '{imp}' found in exception file {py_file.name}"
                    )


def test_domain_application_api_version_isolation() -> None:
    """Verify domain, application, and infrastructure layers have zero API dependencies."""

    app_root = Path(__file__).parent.parent.parent / "app"
    layers_to_check = [
        app_root / "domain",
        app_root / "application",
        app_root / "infrastructure",
    ]

    forbidden_imports = ["app.api", "fastapi", "starlette"]

    for layer_dir in layers_to_check:
        py_files = _get_python_files(layer_dir)
        for py_file in py_files:
            imports = _extract_imported_modules(py_file)
            for imp in imports:
                for forbidden in forbidden_imports:
                    assert not imp.startswith(forbidden), (
                        f"Forbidden API import '{imp}' found in file {py_file.name}"
                    )


def test_middleware_layer_isolation() -> None:
    """Verify domain, application, and infrastructure layers have zero middleware dependencies."""

    app_root = Path(__file__).parent.parent.parent / "app"
    layers_to_check = [
        app_root / "domain",
        app_root / "application",
        app_root / "infrastructure",
    ]

    forbidden_imports = ["app.middleware"]

    for layer_dir in layers_to_check:
        py_files = _get_python_files(layer_dir)
        for py_file in py_files:
            imports = _extract_imported_modules(py_file)
            for imp in imports:
                for forbidden in forbidden_imports:
                    assert not imp.startswith(forbidden), (
                        f"Forbidden middleware import '{imp}' found in file {py_file.name}"
                    )


def test_validation_layer_isolation() -> None:
    """Verify domain, application, and infrastructure layers have zero validation imports."""

    app_root = Path(__file__).parent.parent.parent / "app"
    layers_to_check = [
        app_root / "domain",
        app_root / "application",
        app_root / "infrastructure",
    ]

    forbidden_imports = ["app.schemas.requests", "fastapi.exceptions"]

    for layer_dir in layers_to_check:
        py_files = _get_python_files(layer_dir)
        for py_file in py_files:
            imports = _extract_imported_modules(py_file)
            for imp in imports:
                for forbidden in forbidden_imports:
                    assert not imp.startswith(forbidden), (
                        f"Forbidden validation import '{imp}' found in file {py_file.name}"
                    )


def test_request_id_layer_isolation() -> None:
    """Verify domain layer has zero request ID middleware imports or constants."""
    app_root = Path(__file__).parent.parent.parent / "app"
    layers_to_check = [
        app_root / "domain",
        app_root / "application",
        app_root / "infrastructure",
    ]

    forbidden_imports = ["app.middleware.request_id"]

    for layer_dir in layers_to_check:
        py_files = _get_python_files(layer_dir)
        for py_file in py_files:
            imports = _extract_imported_modules(py_file)
            for imp in imports:
                for forbidden in forbidden_imports:
                    assert not imp.startswith(forbidden), (
                        f"Forbidden RequestID import '{imp}' in file {py_file.name}"
                    )


def test_response_layer_isolation() -> None:
    """Verify domain, application, and infrastructure layers have zero response schema
    or FastAPI Response imports.
    """

    app_root = Path(__file__).parent.parent.parent / "app"
    layers_to_check = [
        app_root / "domain",
        app_root / "application",
        app_root / "infrastructure",
    ]

    forbidden_imports = [
        "app.middleware.response",
        "fastapi.responses",
        "starlette.responses",
    ]

    for layer_dir in layers_to_check:
        py_files = _get_python_files(layer_dir)
        for py_file in py_files:
            imports = _extract_imported_modules(py_file)
            for imp in imports:
                for forbidden in forbidden_imports:
                    assert not imp.startswith(forbidden), (
                        f"Forbidden Response import '{imp}' in file {py_file.name}"
                    )


def test_health_layer_isolation() -> None:
    """Verify domain, application, and infrastructure layers have zero health router imports."""
    app_root = Path(__file__).parent.parent.parent / "app"
    layers_to_check = [
        app_root / "domain",
        app_root / "application",
        app_root / "infrastructure",
    ]

    forbidden_imports = ["app.api.v1.health"]

    for layer_dir in layers_to_check:
        py_files = _get_python_files(layer_dir)
        for py_file in py_files:
            imports = _extract_imported_modules(py_file)
            for imp in imports:
                for forbidden in forbidden_imports:
                    assert not imp.startswith(forbidden), (
                        f"Forbidden Health import '{imp}' in file {py_file.name}"
                    )


def test_readiness_layer_isolation() -> None:
    """Verify domain layer has zero readiness application or HTTP imports, and application
    readiness layer has no HTTP imports.
    """

    app_root = Path(__file__).parent.parent.parent / "app"

    # 1. Domain layer must not import readiness or API concerns
    domain_files = _get_python_files(app_root / "domain")
    for py_file in domain_files:
        imports = _extract_imported_modules(py_file)
        for imp in imports:
            assert not imp.startswith("app.application.services.readiness"), (
                f"Forbidden readiness import '{imp}' in domain file {py_file.name}"
            )
            assert not imp.startswith("app.api"), (
                f"Forbidden API import '{imp}' in domain file {py_file.name}"
            )

    # 2. Application readiness service must not import FastAPI or Starlette HTTP responses
    readiness_files = _get_python_files(app_root / "application" / "services")
    for py_file in readiness_files:
        imports = _extract_imported_modules(py_file)
        for imp in imports:
            assert not imp.startswith("fastapi.responses"), (
                f"Forbidden HTTP response import '{imp}' in application service file {py_file.name}"
            )
            assert not imp.startswith("starlette.responses"), (
                f"Forbidden HTTP response import '{imp}' in application service file {py_file.name}"
            )


def test_documentation_layer_isolation() -> None:
    """Verify domain layer has zero FastAPI, OpenAPI, Swagger, or ReDoc documentation imports."""
    app_root = Path(__file__).parent.parent.parent / "app"

    domain_files = _get_python_files(app_root / "domain")
    forbidden = ["fastapi", "openapi", "swagger", "redoc"]

    for py_file in domain_files:
        imports = _extract_imported_modules(py_file)
        for imp in imports:
            for forb in forbidden:
                assert not imp.startswith(forb), (
                    f"Forbidden documentation import '{imp}' in domain file {py_file.name}"
                )


def test_openapi_layer_isolation() -> None:
    """Verify domain, application, and infrastructure layers have zero imports of
    app.core.openapi.
    """
    app_root = Path(__file__).parent.parent.parent / "app"

    layers = ["domain", "application", "infrastructure"]
    for layer in layers:
        files = _get_python_files(app_root / layer)
        for py_file in files:
            imports = _extract_imported_modules(py_file)
            for imp in imports:
                assert not imp.startswith("app.core.openapi"), (
                    f"Forbidden OpenAPI configuration import '{imp}' in {layer} file {py_file.name}"
                )


def test_service_foundation_layer_isolation() -> None:
    """Verify domain layer has zero imports of FastAPI, Starlette, HTTP, middleware, or secrets."""
    app_root = Path(__file__).parent.parent.parent / "app"

    domain_files = _get_python_files(app_root / "domain")
    forbidden = ["fastapi", "starlette", "httpx", "app.middleware", "app.exceptions.handler"]

    for py_file in domain_files:
        imports = _extract_imported_modules(py_file)
        for imp in imports:
            for forb in forbidden:
                assert not imp.startswith(forb), (
                    f"Forbidden foundation import '{imp}' in domain file {py_file.name}"
                )
