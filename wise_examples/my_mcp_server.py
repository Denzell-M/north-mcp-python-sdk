"""A minimal, working MCP server for the WISE North workshop.

What this file does
- Runs an MCP server over Streamable HTTP (the transport North expects)
- Exposes a few simple tools (add/subtract/multiply/divide + a batch calculator)

How to run locally
  cd wise_examples
  uv run python my_mcp_server.py

Then expose it publicly
  ngrok http 3001

Then register the ngrok URL in North (see wise_examples/README.md).

IMPORTANT: Tool names must be globally unique in North.
Set TOOL_PREFIX to something unique (recommended).
Example:
  export TOOL_PREFIX=denzell_twerdohl_lib

If you don't set TOOL_PREFIX, it defaults to "firstname_lastname".
"""

import os
from typing import List

from north_mcp_python_sdk import NorthMCPServer
from pydantic import BaseModel, Field

# ---- Configuration ----

HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "3001"))

# Tool names MUST be unique across all North users/servers.
# Use something like: first_last, first_last_project, etc.
TOOL_PREFIX = os.getenv("TOOL_PREFIX", "firstname_lastname").strip() or "firstname_lastname"

# ---- Server ----

mcp = NorthMCPServer(
    name="WISE Demo Server",
    host=HOST,
    port=PORT,
)


def _tool_name(suffix: str) -> str:
    """Build a globally-unique tool name."""
    return f"{TOOL_PREFIX}_{suffix}"


# ---- Simple calculator tools ----


@mcp.tool(name=_tool_name("add"))
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool(name=_tool_name("subtract"))
def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b


@mcp.tool(name=_tool_name("multiply"))
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@mcp.tool(name=_tool_name("divide"), annotations={"destructiveHint": True})
def divide(a: int, b: int) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


class CalculationRequest(BaseModel):
    """Pydantic model for batch calculations."""

    operation: str = Field(
        description="Operation to perform: add, subtract, multiply, divide, average"
    )
    numbers: List[float] = Field(description="List of numbers")
    precision: int = Field(default=2, description="Decimal precision for the result")


@mcp.tool(name=_tool_name("batch_calculate"))
def batch_calculate(request: CalculationRequest) -> dict:
    """Perform a batch calculation over a list of numbers."""

    numbers = request.numbers
    operation = request.operation.lower().strip()
    precision = request.precision

    if not numbers:
        return {"error": "No numbers provided"}

    if operation == "add":
        result = sum(numbers)
    elif operation == "subtract":
        result = numbers[0]
        for n in numbers[1:]:
            result -= n
    elif operation == "multiply":
        result = 1.0
        for n in numbers:
            result *= n
    elif operation == "divide":
        result = numbers[0]
        for n in numbers[1:]:
            if n == 0:
                return {"error": "Cannot divide by zero"}
            result /= n
    elif operation == "average":
        result = sum(numbers) / len(numbers)
    else:
        return {"error": f"Unknown operation: {operation}"}

    return {
        "operation": operation,
        "input_numbers": numbers,
        "result": round(float(result), precision),
        "precision": precision,
    }


if __name__ == "__main__":
    # North expects Streamable HTTP for new servers.
    mcp.run(transport="streamable-http")
