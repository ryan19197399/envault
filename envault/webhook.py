"""Webhook notification support for vault events."""
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional


def set_webhook(vault_data: dict, url: str, events: Optional[list] = None) -> None:
    """Register a webhook URL, optionally filtered to specific event types."""
    if "_webhooks" not in vault_data:
        vault_data["_webhooks"] = {}
    vault_data["_webhooks"][url] = {
        "url": url,
        "events": events or ["*"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def remove_webhook(vault_data: dict, url: str) -> bool:
    """Remove a registered webhook. Returns True if it existed."""
    hooks = vault_data.get("_webhooks", {})
    if url in hooks:
        del hooks[url]
        return True
    return False


def list_webhooks(vault_data: dict) -> list:
    """Return all registered webhooks."""
    return list(vault_data.get("_webhooks", {}).values())


def _matches(hook: dict, event: str) -> bool:
    events = hook.get("events", ["*"])
    return "*" in events or event in events


def fire_webhook(vault_data: dict, event: str, payload: Optional[dict] = None) -> list:
    """Send event to all matching webhooks. Returns list of (url, success) tuples."""
    results = []
    body = json.dumps({
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload or {},
    }).encode()
    for hook in vault_data.get("_webhooks", {}).values():
        if not _matches(hook, event):
            continue
        url = hook["url"]
        try:
            req = urllib.request.Request(
                url, data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5):
                pass
            results.append((url, True))
        except Exception:
            results.append((url, False))
    return results
