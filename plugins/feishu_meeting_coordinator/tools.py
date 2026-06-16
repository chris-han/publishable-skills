from __future__ import annotations

import importlib.util
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any


def _ok(key: str, value: Any) -> str:
    return json.dumps({"ok": True, key: value}, ensure_ascii=False, sort_keys=True)


def _error(message: str) -> str:
    return json.dumps({"ok": False, "error": message}, ensure_ascii=False, sort_keys=True)


def _gateway(kwargs: dict[str, Any]):
    gateway = kwargs.get("gateway")
    if gateway is None:
        raise RuntimeError("Semantier gateway binding required")
    return gateway


@lru_cache(maxsize=1)
def _feishu_helper():
    helper_path = Path(__file__).with_name("scripts") / "feishu_bot_api.py"
    spec = importlib.util.spec_from_file_location(
        "feishu_meeting_coordinator_feishu_bot_api",
        helper_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Feishu helper script: {helper_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _helper_call(func_name: str, *args: Any, **kwargs: Any) -> str:
    try:
        result = getattr(_feishu_helper(), func_name)(*args, **kwargs)
    except Exception as exc:
        payload = getattr(exc, "payload", None)
        if isinstance(payload, dict) and payload:
            return json.dumps(
                {"ok": False, "error": str(exc), "payload": payload},
                ensure_ascii=False,
                sort_keys=True,
            )
        return _error(str(exc))
    return _ok("result", result)


def _payload(args: Any) -> dict[str, Any]:
    if args is None:
        return {}
    if not isinstance(args, dict):
        raise RuntimeError("tool args must be a JSON object")
    return dict(args)


def _list_arg(payload: dict[str, Any], *names: str) -> list[Any]:
    for name in names:
        value = payload.get(name)
        if value is None:
            continue
        if isinstance(value, list):
            return value
        return [value]
    return []


def feishu_contacts_search(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "search_contacts",
        str(payload.get("query") or ""),
        limit=int(payload.get("limit") or 10),
    )


def feishu_chats_search(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "search_chats",
        str(payload.get("query") or ""),
        limit=int(payload.get("limit") or 10),
    )


def feishu_chat_members_get(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "get_chat_members",
        str(payload.get("chat_id") or ""),
        member_id_type=str(payload.get("member_id_type") or "open_id"),
    )


def feishu_meeting_create(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "create_meeting",
        title=str(payload.get("title") or ""),
        start_time=str(payload.get("start_time") or ""),
        end_time=str(payload.get("end_time") or ""),
        attendees=_list_arg(payload, "attendees", "attendee"),
        timezone=str(payload.get("timezone") or "Asia/Shanghai"),
        description=payload.get("description"),
        location=payload.get("location"),
        idempotency_key=payload.get("idempotency_key"),
        requester_open_id=payload.get("requester_open_id"),
        requester_calendar_id=payload.get("requester_calendar_id"),
    )


def feishu_meeting_negotiation_start(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "start_negotiation",
        title=str(payload.get("title") or ""),
        requester_open_id=str(payload.get("requester_open_id") or ""),
        attendee_open_ids=[
            str(item) for item in _list_arg(payload, "attendee_open_ids", "attendee_open_id")
        ],
        candidate_slots=[
            str(item) for item in _list_arg(payload, "candidate_slots", "candidate_slot")
        ],
        duration_minutes=int(payload.get("duration_minutes") or 0),
        timezone=str(payload.get("timezone") or "Asia/Shanghai"),
        max_rounds=int(payload.get("max_rounds") or 3),
    )


def feishu_meeting_negotiation_next_round_prompts(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "next_round_prompts",
        payload.get("state") or payload.get("state_payload") or {},
    )


def feishu_meeting_negotiation_submit_response(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "submit_attendee_response",
        payload.get("state") or payload.get("state_payload") or {},
        attendee_open_id=str(payload.get("attendee_open_id") or ""),
        accepted_slots=[str(item) for item in _list_arg(payload, "accepted_slots", "accepted_slot")],
        declined_slots=[str(item) for item in _list_arg(payload, "declined_slots", "declined_slot")],
        note=payload.get("note"),
    )


def feishu_meeting_negotiation_finalize(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "finalize_negotiation_and_create_meeting",
        payload.get("state") or payload.get("state_payload") or {},
        description=payload.get("description"),
        location=payload.get("location"),
    )


def feishu_meeting_attendee_status_list(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "list_attendee_status",
        event_id=str(payload.get("event_id") or ""),
        calendar_id=payload.get("calendar_id"),
        requester_open_id=payload.get("requester_open_id"),
        page_size=int(payload.get("page_size") or 50),
    )


def feishu_final_invitations_send(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "send_final_invitations",
        attendee_open_ids=[
            str(item) for item in _list_arg(payload, "attendee_open_ids", "attendee_open_id")
        ],
        title=str(payload.get("title") or ""),
        start_time=str(payload.get("start_time") or ""),
        end_time=str(payload.get("end_time") or ""),
        timezone=str(payload.get("timezone") or "Asia/Shanghai"),
        meeting_link=payload.get("meeting_link"),
    )


def feishu_attendee_message_send(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "send_attendee_message",
        attendee_open_ids=[str(item) for item in _list_arg(payload, "attendee_open_ids", "attendee_open_id")],
        message=str(payload.get("message") or ""),
    )


def feishu_meeting_new_time_propose(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "propose_new_time",
        attendee_open_ids=[str(item) for item in _list_arg(payload, "attendee_open_ids", "attendee_open_id")],
        title=str(payload.get("title") or ""),
        candidate_slots=[str(item) for item in _list_arg(payload, "candidate_slots", "candidate_slot")],
        timezone=str(payload.get("timezone") or "Asia/Shanghai"),
        event_id=payload.get("event_id"),
        current_time=payload.get("current_time"),
        note=payload.get("note"),
    )


def feishu_meeting_time_update(args, **kwargs):
    payload = _payload(args)
    return _helper_call(
        "update_meeting_time",
        event_id=str(payload.get("event_id") or ""),
        calendar_id=str(payload.get("calendar_id") or ""),
        start_time=str(payload.get("start_time") or ""),
        end_time=str(payload.get("end_time") or ""),
        timezone=str(payload.get("timezone") or "Asia/Shanghai"),
    )


def feishu_meeting_monitor_start(args, **kwargs):
    try:
        monitor = _gateway(kwargs).start_monitor(dict(args or {}))
    except Exception as exc:
        return _error(str(exc))
    return _ok("monitor", monitor)


def feishu_meeting_monitor_tick(args, **kwargs):
    try:
        result = _gateway(kwargs).monitor_tick(dict(args or {}))
    except Exception as exc:
        return _error(str(exc))
    return _ok("result", result)


def feishu_meeting_monitor_stop(args, **kwargs):
    try:
        result = _gateway(kwargs).monitor_stop(dict(args or {}))
    except Exception as exc:
        return _error(str(exc))
    return _ok("result", result)


def feishu_meeting_escalation_retry_tick(args, **kwargs):
    try:
        result = _gateway(kwargs).escalation_retry_tick(dict(args or {}))
    except Exception as exc:
        return _error(str(exc))
    return _ok("result", result)


def feishu_meeting_delivery_task_requeue(args, **kwargs):
    payload = dict(args or {})
    delivery_task_id = str(payload.get("delivery_task_id") or "").strip()
    reason = str(payload.get("reason") or "operator requested requeue").strip()
    if not delivery_task_id:
        return _error("delivery_task_id is required")
    try:
        task = _gateway(kwargs).requeue_delivery_task(
            delivery_task_id=delivery_task_id,
            reason=reason,
        )
    except Exception as exc:
        return _error(str(exc))
    return _ok("delivery_task", task)
