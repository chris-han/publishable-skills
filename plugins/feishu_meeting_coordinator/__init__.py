from __future__ import annotations

from pathlib import Path

from .cli import command, register_cli
from .tools import (
    feishu_attendee_message_send,
    feishu_chat_members_get,
    feishu_chats_search,
    feishu_contacts_search,
    feishu_final_invitations_send,
    feishu_meeting_attendee_status_list,
    feishu_meeting_create,
    feishu_meeting_delivery_task_requeue,
    feishu_meeting_escalation_retry_tick,
    feishu_meeting_monitor_start,
    feishu_meeting_monitor_stop,
    feishu_meeting_monitor_tick,
    feishu_meeting_negotiation_finalize,
    feishu_meeting_negotiation_next_round_prompts,
    feishu_meeting_negotiation_start,
    feishu_meeting_negotiation_submit_response,
    feishu_meeting_new_time_propose,
    feishu_meeting_time_update,
)


_TOOL_SCHEMA = {"type": "object", "properties": {}, "additionalProperties": True}


def register(ctx) -> None:
    ctx.register_skill(
        name="feishu-bot-meeting-coordinator",
        path=Path(__file__).with_name("SKILL.md"),
        description="Book Feishu meetings and start RSVP monitoring via the bundled plugin.",
    )
    ctx.register_tool(
        name="feishu_contacts_search",
        handler=feishu_contacts_search,
        description="Search Feishu contacts by name, email, or open_id using the governed bot configuration.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_chats_search",
        handler=feishu_chats_search,
        description="Search Feishu chats/groups visible to the bot.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_chat_members_get",
        handler=feishu_chat_members_get,
        description="List members of a Feishu chat/group as open_id values.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_create",
        handler=feishu_meeting_create,
        description="Create an online Feishu calendar meeting and send attendee invitations.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_negotiation_start",
        handler=feishu_meeting_negotiation_start,
        description="Start a multi-round Feishu meeting time negotiation.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_negotiation_next_round_prompts",
        handler=feishu_meeting_negotiation_next_round_prompts,
        description="Build attendee prompts for the current negotiation round.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_negotiation_submit_response",
        handler=feishu_meeting_negotiation_submit_response,
        description="Record one attendee response for a Feishu meeting time negotiation.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_negotiation_finalize",
        handler=feishu_meeting_negotiation_finalize,
        description="Finalize an agreed Feishu meeting negotiation and create the calendar event.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_attendee_status_list",
        handler=feishu_meeting_attendee_status_list,
        description="Read live RSVP status for a Feishu calendar event.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_final_invitations_send",
        handler=feishu_final_invitations_send,
        description="Send final Feishu meeting confirmation messages to attendee open_id values.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_attendee_message_send",
        handler=feishu_attendee_message_send,
        description="Send a direct Feishu text message to attendee open_id values.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_new_time_propose",
        handler=feishu_meeting_new_time_propose,
        description="Send attendees a Feishu message proposing replacement meeting times.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_time_update",
        handler=feishu_meeting_time_update,
        description="Update a Feishu meeting event start and end time.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_monitor_start",
        handler=feishu_meeting_monitor_start,
        description="Start or repair RSVP monitoring for a Feishu meeting revision.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_monitor_tick",
        handler=feishu_meeting_monitor_tick,
        description="Run one RSVP monitor tick.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_monitor_stop",
        handler=feishu_meeting_monitor_stop,
        description="Stop one RSVP monitor and remove its cron job.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_escalation_retry_tick",
        handler=feishu_meeting_escalation_retry_tick,
        description="Retry pending creator escalation delivery tasks.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_tool(
        name="feishu_meeting_delivery_task_requeue",
        handler=feishu_meeting_delivery_task_requeue,
        description="Requeue a failed creator escalation delivery task and heal the retry cron.",
        schema=_TOOL_SCHEMA,
        toolset="meeting-coordinator",
    )
    ctx.register_cli_command(
        name="feishu-meeting-coordinator",
        help="Inspect and operate Feishu meeting RSVP monitors",
        setup_fn=register_cli,
        handler_fn=command,
        description="Operator CLI for Feishu meeting RSVP monitoring.",
    )
