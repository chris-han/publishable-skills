---
name: feishu-bot-meeting-coordinator
description: >
  Book Feishu meetings, query RSVP status, and start automatic RSVP monitoring
  through the bundled plugin.
version: 1.0.0
author: Semantier
license: MIT
tags:
  - feishu
  - calendar
  - meetings
  - contacts
---

# Feishu Bot Meeting Coordinator

When a user books or updates a Feishu meeting, create or update the calendar event and then call `feishu_meeting_monitor_start` with the returned `event_id`, `calendar_id`, `event_revision_id`, attendees, and captured `creator_delivery_binding`.

When a user asks for RSVP status, call live Feishu attendee status first. Do not infer RSVP state from memory.

The plugin handles follow-up reminders, creator escalation, delivery retry, and cron repair.

Use the registered Feishu tools directly for contact lookup, chat lookup, meeting creation, attendee messaging, direct RSVP checks, replacement slot proposals, and meeting-time updates:

- `feishu_contacts_search`
- `feishu_chats_search`
- `feishu_chat_members_get`
- `feishu_meeting_create`
- `feishu_meeting_negotiation_start`
- `feishu_meeting_negotiation_next_round_prompts`
- `feishu_meeting_negotiation_submit_response`
- `feishu_meeting_negotiation_finalize`
- `feishu_meeting_attendee_status_list`
- `feishu_final_invitations_send`
- `feishu_attendee_message_send`
- `feishu_meeting_new_time_propose`
- `feishu_meeting_time_update`

Do not use terminal, `write_file`, `execute_code`, generated Python, generated shell scripts, raw HTTP calls, or temporary files such as `/tmp/create_feishu_meeting.py` for Feishu meeting, contact, chat, or calendar operations. Do not synthesize commands such as `hermes feishu ...` or `python .../feishu_bot_api.py ...`.

If one of the registered Feishu tools needed for the task is unavailable, stop and report that the Feishu meeting-coordinator tool surface is not loaded. Do not work around the missing tool by generating code at runtime.

The plugin tools call `scripts/feishu_bot_api.py` directly. The returned `user_id` / `message_user_id` values from RSVP lookups are Feishu `open_id` values and can be passed directly into direct-message follow-up tooling.
