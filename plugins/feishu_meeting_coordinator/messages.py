from __future__ import annotations

from pathlib import Path


def _prompt_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "src" / "prompts" / "meeting_coordinator"
        if candidate.exists():
            return candidate
    raise RuntimeError("meeting coordinator prompt assets not found")


def _render(template_name: str, values: dict[str, str]) -> str:
    text = (_prompt_root() / template_name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def render_followup_message(
    *,
    attendee_name: str,
    meeting_title: str,
    start_time: str,
    organizer_name: str,
    response_status: str,
) -> str:
    return _render(
        "FOLLOWUP_MESSAGE.md",
        {
            "attendee_name": attendee_name,
            "meeting_title": meeting_title,
            "start_time": start_time,
            "organizer_name": organizer_name,
            "response_status": response_status,
        },
    )


def render_creator_escalation(
    *,
    creator_name: str,
    attendee_name: str,
    meeting_title: str,
    reason: str,
) -> str:
    return _render(
        "CREATOR_ESCALATION.md",
        {
            "creator_name": creator_name,
            "attendee_name": attendee_name,
            "meeting_title": meeting_title,
            "reason": reason,
        },
    )
