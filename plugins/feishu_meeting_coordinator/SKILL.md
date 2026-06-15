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

Use the bundled Feishu helper surfaces for contact lookup, attendee messaging, direct RSVP checks, replacement slot proposals, and meeting-time updates. The returned `user_id` / `message_user_id` values from RSVP lookups are Feishu `open_id` values and can be passed directly into direct-message follow-up tooling.
