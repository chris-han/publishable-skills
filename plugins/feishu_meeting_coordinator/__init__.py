from __future__ import annotations

from .cli import command, register_cli
from .tools import (
    feishu_meeting_delivery_task_requeue,
    feishu_meeting_escalation_retry_tick,
    feishu_meeting_monitor_start,
    feishu_meeting_monitor_stop,
    feishu_meeting_monitor_tick,
)


def register(ctx) -> None:
    ctx.register_tool(
        name="feishu_meeting_monitor_start",
        handler=feishu_meeting_monitor_start,
        description="Start or repair RSVP monitoring for a Feishu meeting revision.",
        schema=None,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_monitor_tick",
        handler=feishu_meeting_monitor_tick,
        description="Run one RSVP monitor tick.",
        schema=None,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_monitor_stop",
        handler=feishu_meeting_monitor_stop,
        description="Stop one RSVP monitor and remove its cron job.",
        schema=None,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_escalation_retry_tick",
        handler=feishu_meeting_escalation_retry_tick,
        description="Retry pending creator escalation delivery tasks.",
        schema=None,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_delivery_task_requeue",
        handler=feishu_meeting_delivery_task_requeue,
        description="Requeue a failed creator escalation delivery task and heal the retry cron.",
        schema=None,
        toolset="meeting-coordinator",
    )
    ctx.register_cli_command(
        name="feishu-meeting-coordinator",
        help="Inspect and operate Feishu meeting RSVP monitors",
        setup_fn=register_cli,
        handler_fn=command,
        description="Operator CLI for Feishu meeting RSVP monitoring.",
    )
