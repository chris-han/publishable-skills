# Semantier Skills

Standalone GitHub-backed skill catalog for Semantier and Hermes installation flows.

## Included Skills

- `feishu-bot-meeting-coordinator`

## Skill Layout

This repository follows the Hermes Agent skill spec:

```text
skills/
└── productivity/
    └── feishu-bot-meeting-coordinator/
        ├── SKILL.md
        └── scripts/
            └── feishu_bot_api.py
```

## Install Identifiers

The current Feishu skill is installable from this repository with:

```text
chris-han/semantier-skills/skills/productivity/feishu-bot-meeting-coordinator
```

## Marketplace URL

Use this repository URL directly in the Skills screen marketplace URL setting:

```text
https://github.com/chris-han/semantier-skills
```

The workspace marketplace search now treats that GitHub repo URL as a skill catalog and searches the repo's `skills/` tree.