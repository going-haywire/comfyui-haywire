# SPDX-License-Identifier: GPL-3.0-or-later
"""Parameter types and value parsing; no ComfyUI imports, so it can be tested on its own."""

from __future__ import annotations

from typing import Any

#: Types of a Haywire Parameter. Haywire maps them to INT / FLOAT / BOOL / STRING / choice ports.
PARAMETER_TYPES = ("number", "integer", "toggle", "text", "prompt", "choice")


def parse_value(param_type: str, text: Any) -> Any:
    """The typed value of a parameter's ``default``, which the node stores as text."""
    raw = "" if text is None else str(text).strip()
    if param_type == "number":
        return float(raw) if raw else 0.0
    if param_type == "integer":
        return int(float(raw)) if raw else 0
    if param_type == "toggle":
        return raw.lower() in ("true", "1", "yes", "on")
    if param_type in PARAMETER_TYPES:
        return "" if text is None else str(text)
    raise ValueError(f"unknown parameter type {param_type!r}")
