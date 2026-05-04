import pytest

from src.agent.registry import ToolRegistry

# ── Registry tests ────────────────────────────────────────────────────────────


def test_tool_decorator_registers_function():
    reg = ToolRegistry()

    @reg.tool({"type": "object", "properties": {"x": {"type": "integer"}}, "required": ["x"]})
    def my_func(x: int, context=None) -> int:
        """Double x."""
        return x * 2

    assert "my_func" in reg._tools


def test_registry_schemas_returns_openai_format():
    reg = ToolRegistry()

    @reg.tool({"type": "object", "properties": {"x": {"type": "integer"}}, "required": ["x"]})
    def add_one(x: int, context=None) -> int:
        """Add one to x."""
        return x + 1

    schemas = reg.schemas()
    assert len(schemas) == 1
    schema = schemas[0]
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "add_one"
    assert schema["function"]["description"] == "Add one to x."
    assert schema["function"]["parameters"]["properties"]["x"]["type"] == "integer"


def test_registry_dispatch_calls_function_with_context():
    reg = ToolRegistry()

    class FakeContext:
        value = 0

    @reg.tool({"type": "object", "properties": {"n": {"type": "integer"}}, "required": ["n"]})
    def set_value(n: int, context=None) -> dict:
        """Set context value."""
        context.value = n
        return {"set": n}

    ctx = FakeContext()
    result = reg.dispatch("set_value", {"n": 42}, ctx)
    assert result == {"set": 42}
    assert ctx.value == 42


def test_registry_dispatch_raises_on_unknown_tool():
    reg = ToolRegistry()
    with pytest.raises(KeyError):
        reg.dispatch("nonexistent", {}, None)
