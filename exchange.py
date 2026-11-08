# SPDX-License-Identifier: GPL-3.0-or-later
"""The workflow exchange: ComfyUI pages publish, haywire subscribes. No ComfyUI imports.

Each publisher (a ComfyUI page, by its client id) holds one current workflow. A new
subscriber is sent every current workflow at once, then each new publish.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

#: Bumped when a message or route changes shape; haywire checks it at GET /api/haywire/version.
PROTOCOL = 1

#: Websocket message type sent to subscribers.
PUBLISHED = "haywire_workflow_published"


@dataclass
class Exchange:
    """Current workflows and subscribers, in memory; ComfyUI's routes drive it."""

    workflows: dict[str, dict[str, Any]] = field(default_factory=dict)
    subscribers: set[str] = field(default_factory=set)

    def publish(self, client_id: str, name: str, workflow: dict[str, Any]) -> list[tuple[str, dict]]:
        """Store *workflow* as *client_id*'s current one; return (subscriber, message) to send."""
        if not isinstance(workflow, dict):
            raise ValueError("workflow must be an API-format object")
        message = {"publisher": {"name": name, "id": client_id}, "workflow": workflow}
        self.workflows[client_id] = message
        return [(sid, message) for sid in sorted(self.subscribers)]

    def subscribe(self, client_id: str) -> list[tuple[str, dict]]:
        """Add *client_id*; return the current workflows to send to it."""
        self.subscribers.add(client_id)
        return [(client_id, m) for m in self.workflows.values()]

    def unsubscribe(self, client_id: str) -> None:
        self.subscribers.discard(client_id)

    def withdraw(self, client_id: str) -> None:
        """Forget *client_id*'s workflow, e.g. when its page closes."""
        self.workflows.pop(client_id, None)

    def listing(self) -> list[dict]:
        return [{"publisher": m["publisher"], "nodes": len(m["workflow"])} for m in self.workflows.values()]
