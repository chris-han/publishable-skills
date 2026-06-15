from __future__ import annotations


def register_cli(parser) -> None:
    parser.add_parser("monitors")


def command(args) -> int:
    print("feishu meeting coordinator")
    return 0
