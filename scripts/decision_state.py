#!/usr/bin/env python3
"""Persist and render a Let Him Grill decision graph."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TYPES = {"auto", "review", "human", "derived", "blocked"}
STATUSES = {"recommended", "confirmed", "pending", "derived", "invalidated"}
OPTION_TRIAGES = {
    "recommended",
    "solid-alternative",
    "situational",
    "not-recommended",
    "excluded",
}
LEVELS = {"low", "medium", "high"}
STATE_VERSION = 2
TEMPLATE = Path(__file__).parent.parent / "assets" / "decision-tree.html"


def load(path: Path) -> dict:
    try:
        state = json.loads(path.read_text())
    except FileNotFoundError as error:
        raise SystemExit(f"State not found: {path}") from error
    validate(state)
    return state


def save(path: Path, state: dict) -> None:
    validate(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def validate(state: dict) -> None:
    if state.get("version") != STATE_VERSION or not isinstance(state.get("nodes"), list):
        raise SystemExit(f"Invalid state: expected version {STATE_VERSION} and nodes list")
    ids = [node.get("id") for node in state["nodes"]]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise SystemExit("Invalid state: node IDs must be unique and non-empty")
    known = set(ids)
    for node in state["nodes"]:
        if node.get("type") not in TYPES or node.get("status") not in STATUSES:
            raise SystemExit(f"Invalid type or status on node {node['id']}")
        if node.get("actor") not in {None, "ai", "human"}:
            raise SystemExit(f"Invalid actor on node {node['id']}")
        options = node.get("options", [])
        option_ids = [option.get("id") for option in options]
        if (
            not options
            or len(option_ids) != len(set(option_ids))
            or any(not option.get("label") for option in options)
        ):
            raise SystemExit(f"Invalid options on node {node['id']}")
        if node.get("choice") is not None and node["choice"] not in option_ids:
            raise SystemExit(f"Unknown choice on node {node['id']}")
        for option in options:
            assessment = option.get("assessment")
            if not isinstance(assessment, dict):
                raise SystemExit(f"Missing assessment on option {option.get('id')}")
            if assessment.get("status") not in {None, "invalidated"}:
                raise SystemExit(f"Invalid assessment status on option {option['id']}")
            if assessment.get("triage") not in OPTION_TRIAGES:
                raise SystemExit(f"Invalid triage on option {option['id']}")
            if assessment.get("risk") not in LEVELS or assessment.get("effort") not in LEVELS:
                raise SystemExit(f"Invalid risk or effort on option {option['id']}")
            if not isinstance(assessment.get("reversible"), bool):
                raise SystemExit(f"Invalid reversibility on option {option['id']}")
            if not all(isinstance(assessment.get(key), str) and assessment[key] for key in ("reason", "impact", "preferredWhen")):
                raise SystemExit(f"Incomplete assessment on option {option['id']}")
            option_confidence = assessment.get("confidence")
            if not isinstance(option_confidence, (int, float)) or not 0 <= option_confidence <= 1:
                raise SystemExit(f"Invalid confidence on option {option['id']}")
        if not set(node.get("dependsOn", [])) <= known - {node["id"]}:
            raise SystemExit(f"Unknown or self dependency on node {node['id']}")
        confidence = node.get("confidence")
        if confidence is not None and not 0 <= confidence <= 1:
            raise SystemExit(f"Confidence outside 0..1 on node {node['id']}")


def parse_option(value: str) -> dict:
    option_id, separator, option_text = value.partition("=")
    label, description_separator, description = option_text.partition("::")
    if not separator or not option_id.strip() or not label.strip():
        raise argparse.ArgumentTypeError("option must be id=Label or id=Label::Description")
    option = {"id": option_id.strip(), "label": label.strip()}
    if description_separator and description.strip():
        option["description"] = description.strip()
    return option


def parse_assessment(value: str) -> tuple[str, dict]:
    option_id, separator, payload = value.partition("=")
    if not separator or not option_id.strip():
        raise argparse.ArgumentTypeError("assessment must be option-id={JSON}")
    try:
        assessment = json.loads(payload)
    except json.JSONDecodeError as error:
        raise argparse.ArgumentTypeError(f"invalid assessment JSON: {error.msg}") from error
    if not isinstance(assessment, dict):
        raise argparse.ArgumentTypeError("assessment JSON must be an object")
    return option_id.strip(), assessment


def initial_status(node_type: str, choice: str | None) -> str:
    if node_type == "human" and choice is None:
        return "pending"
    if node_type == "derived":
        return "derived"
    return "recommended" if choice else "pending"


def command_init(args: argparse.Namespace) -> None:
    path = Path(args.state)
    if path.exists() and not args.force:
        raise SystemExit(f"State already exists: {path}; use --force to replace")
    save(path, {"version": STATE_VERSION, "title": args.title, "nodes": []})


def command_add(args: argparse.Namespace) -> None:
    path = Path(args.state)
    state = load(path)
    existing = next((node for node in state["nodes"] if node["id"] == args.id), None)
    if existing and not args.replace:
        raise SystemExit(f"Node already exists: {args.id}; use --replace")
    assessments = dict(args.assessment)
    option_ids = {option["id"] for option in args.option}
    if set(assessments) != option_ids:
        raise SystemExit("Provide exactly one --assessment for every option")
    options = [option | {"assessment": assessments[option["id"]]} for option in args.option]
    choice = args.choice
    if args.type == "auto" and choice is None:
        safe = [
            option for option in options
            if option["assessment"]["triage"] == "recommended"
            and option["assessment"]["risk"] == "low"
            and option["assessment"]["reversible"] is True
        ]
        if len(safe) == 1:
            choice = safe[0]["id"]
        else:
            raise SystemExit("An auto decision requires exactly one low-risk reversible recommendation")
    if choice:
        selected = next((option for option in options if option["id"] == choice), None)
        if selected is None:
            raise SystemExit(f"Unknown choice on node {args.id}: {choice}")
        selected_assessment = selected["assessment"]
        if selected_assessment["triage"] == "excluded":
            raise SystemExit("Refusing to auto-select an excluded option")
    else:
        selected_assessment = None
    node = {
        "id": args.id,
        "question": args.question,
        "type": args.type,
        "options": options,
        "choice": choice,
        "reason": args.reason,
        "confidence": args.confidence if args.confidence is not None else selected_assessment and selected_assessment["confidence"],
        "reversible": args.reversible or bool(selected_assessment and selected_assessment["reversible"]),
        "dependsOn": args.depends_on,
        "status": initial_status(args.type, choice),
        "actor": "ai" if choice else None,
    }
    if existing:
        if existing.get("actor") == "human" and existing.get("choice") != choice:
            raise SystemExit("Refusing to overwrite a confirmed human choice; use choose")
        state["nodes"][state["nodes"].index(existing)] = node
    else:
        state["nodes"].append(node)
    save(path, state)


def descendants(state: dict, node_id: str) -> set[str]:
    found: set[str] = set()
    changed = True
    while changed:
        changed = False
        for node in state["nodes"]:
            if node["id"] not in found and (
                node_id in node.get("dependsOn", [])
                or found.intersection(node.get("dependsOn", []))
            ):
                found.add(node["id"])
                changed = True
    return found


def command_choose(args: argparse.Namespace) -> None:
    path = Path(args.state)
    state = load(path)
    node = next((item for item in state["nodes"] if item["id"] == args.node), None)
    if node is None:
        raise SystemExit(f"Unknown node: {args.node}")
    if args.option not in {option["id"] for option in node["options"]}:
        raise SystemExit(f"Unknown option for {args.node}: {args.option}")
    selected = next(option for option in node["options"] if option["id"] == args.option)
    if selected["assessment"].get("status") == "invalidated":
        raise SystemExit("Refusing to select a stale option; reassess the node first")
    if selected["assessment"]["triage"] == "excluded":
        raise SystemExit("Refusing to select an excluded option; reassess it first")
    changed = node.get("choice") != args.option
    node["choice"] = args.option
    node["actor"] = args.actor
    node["status"] = "confirmed" if args.actor == "human" else "recommended"
    if changed:
        for item in state["nodes"]:
            if item["id"] in descendants(state, args.node):
                item["choice"] = None
                item["actor"] = None
                item["status"] = "invalidated"
                item["reason"] = "Earlier dependency changed; reassessment required."
                item["confidence"] = None
                for option in item["options"]:
                    option["assessment"]["status"] = "invalidated"
    save(path, state)


def option_label(node: dict, choice: str | None = None) -> str:
    selected = choice if choice is not None else node.get("choice")
    return next(
        (option["label"] for option in node["options"] if option["id"] == selected),
        "No selection yet",
    )


def render_html(state: dict, state_path: Path) -> str:
    template = TEMPLATE.read_text()
    state_json = json.dumps(state, ensure_ascii=False).replace("<", "\\u003c")
    path_json = json.dumps(str(state_path.resolve()), ensure_ascii=False).replace("<", "\\u003c")
    return template.replace("__LET_HIM_GRILL_STATE_JSON__", state_json).replace(
        "__LET_HIM_GRILL_STATE_PATH_JSON__", path_json
    )


def command_render(args: argparse.Namespace) -> None:
    state_path = Path(args.state)
    state = load(state_path)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(state, state_path))


def command_export(args: argparse.Namespace) -> None:
    state = load(Path(args.state))
    lines = [f"# {state.get('title', 'Decision path')}", ""]
    for node in state["nodes"]:
        lines.extend(
            [
                f"## {node['question']}",
                "",
                f"- Type: `{node['type']}`",
                f"- Status: `{node['status']}`",
                f"- Choice: {option_label(node)}",
                f"- Reason: {node.get('reason') or 'Open'}",
                "",
            ]
        )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(required=True)
    init = commands.add_parser("init")
    init.add_argument("state")
    init.add_argument("--title", required=True)
    init.add_argument("--force", action="store_true")
    init.set_defaults(function=command_init)

    add = commands.add_parser("add")
    add.add_argument("state")
    add.add_argument("--id", required=True)
    add.add_argument("--question", required=True)
    add.add_argument("--type", choices=sorted(TYPES), required=True)
    add.add_argument("--option", action="append", type=parse_option, required=True)
    add.add_argument("--assessment", action="append", type=parse_assessment, required=True)
    add.add_argument("--choice")
    add.add_argument("--reason")
    add.add_argument("--confidence", type=float)
    add.add_argument("--reversible", action="store_true")
    add.add_argument("--depends-on", action="append", default=[])
    add.add_argument("--replace", action="store_true")
    add.set_defaults(function=command_add)

    choose = commands.add_parser("choose")
    choose.add_argument("state")
    choose.add_argument("node")
    choose.add_argument("option")
    choose.add_argument("--actor", choices=("human", "ai"), default="human")
    choose.set_defaults(function=command_choose)

    render = commands.add_parser("render")
    render.add_argument("state")
    render.add_argument("output")
    render.set_defaults(function=command_render)

    export = commands.add_parser("export")
    export.add_argument("state")
    export.add_argument("output")
    export.set_defaults(function=command_export)
    return root


def main() -> None:
    args = parser().parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
