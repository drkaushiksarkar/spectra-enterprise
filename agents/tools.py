"""Tool registry and decorator pattern for agent-callable functions.

Provides a declarative interface for registering Python functions as
tools that can be discovered and invoked by AI agents. Automatically
generates JSON Schema from type annotations and docstrings.
"""

from __future__ import annotations

import functools
import inspect
import logging
from typing import Any, Callable, TypeVar, get_type_hints

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

_GLOBAL_REGISTRY: dict[str, dict[str, Any]] = {}


def tool(
    name: str | None = None,
    description: str | None = None,
) -> Callable[[F], F]:
    """Decorator to register a function as an agent-callable tool.

    Automatically extracts parameter schema from type annotations.
    Uses the function docstring as description if not provided.

    Usage:
        @tool(name="search_indicators")
        def search_indicators(query: str, limit: int = 10) -> list[dict]:
            '''Search health indicators by keyword.'''
            ...
    """

    def decorator(func: F) -> F:
        tool_name = name or func.__name__
        tool_desc = description or (func.__doc__ or "").strip().split("\n")[0]

        hints = get_type_hints(func)
        sig = inspect.signature(func)

        properties: dict[str, Any] = {}
        required: list[str] = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            param_type = hints.get(param_name, Any)
            schema = _type_to_schema(param_type)

            if param.default is inspect.Parameter.empty:
                required.append(param_name)
            else:
                schema["default"] = param.default

            properties[param_name] = schema

        _GLOBAL_REGISTRY[tool_name] = {
            "name": tool_name,
            "description": tool_desc,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
            "handler": func,
        }

        logger.info("Registered tool: %s", tool_name)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.debug("Executing tool: %s", tool_name)
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def _type_to_schema(annotation: Any) -> dict[str, Any]:
    """Convert a Python type annotation to JSON Schema."""
    type_map: dict[type, str] = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
    }

    if annotation in type_map:
        return {"type": type_map[annotation]}

    origin = getattr(annotation, "__origin__", None)

    if origin is list:
        args = getattr(annotation, "__args__", (Any,))
        return {"type": "array", "items": _type_to_schema(args[0]) if args else {}}

    if origin is dict:
        return {"type": "object"}

    return {"type": "string"}


def get_tool(name: str) -> dict[str, Any]:
    if name not in _GLOBAL_REGISTRY:
        raise KeyError(f"Tool not found: {name}")
    return _GLOBAL_REGISTRY[name]


def list_tools() -> list[dict[str, Any]]:
    return [
        {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}
        for t in _GLOBAL_REGISTRY.values()
    ]


def execute_tool(name: str, **kwargs: Any) -> Any:
    entry = get_tool(name)
    handler = entry["handler"]
    required = entry["parameters"].get("required", [])
    for r in required:
        if r not in kwargs:
            raise ValueError(f"Missing required parameter '{r}' for tool '{name}'")
    return handler(**kwargs)


def clear_registry() -> None:
    _GLOBAL_REGISTRY.clear()
