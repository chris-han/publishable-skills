from __future__ import annotations

from typing import Any


def list_monitors(*, workspace_id: str, limit: int = 50, store: Any | None = None) -> dict[str, Any]:
    from agents import meeting_coordinator_store

    active_store = store or meeting_coordinator_store.MeetingCoordinatorStore()
    return {
        "monitors": active_store.list_operation_monitors(workspace_id=workspace_id, limit=limit),
        "delivery_tasks": active_store.list_operation_delivery_tasks(workspace_id=workspace_id, limit=limit),
        "workspace_state": active_store.get_workspace_state(workspace_id),
    }


def retry_delivery_now(*, workspace_id: str, store: Any, delivery_client: Any) -> dict[str, Any]:
    from agents import meeting_coordinator_gateway

    return meeting_coordinator_gateway.escalation_retry_tick(
        {"workspace_id": workspace_id},
        store=store,
        delivery_client=delivery_client,
    )


def requeue_delivery_task(*, delivery_task_id: str, reason: str, store: Any, cron: Any) -> dict[str, Any]:
    from agents import meeting_coordinator_gateway

    return meeting_coordinator_gateway.requeue_delivery_task(
        delivery_task_id=delivery_task_id,
        reason=reason,
        store=store,
        cron=cron,
    )
