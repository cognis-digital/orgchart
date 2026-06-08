"""Command-line interface for ORGCHART.

Subcommands:
  tree      render the reporting tree
  metrics   per-employee span-of-control / depth / headcount roll-up
  summary   org-wide headcount + structure summary
  validate  check structural integrity, exit non-zero on problems

Global options: --version, --format {table,json}.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import TOOL_NAME, TOOL_VERSION
from .core import OrgError, build_org, parse_csv, render_tree


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _load(path: str):
    return build_org(parse_csv(_read_input(path)))


def _emit_json(obj) -> None:
    print(json.dumps(obj, indent=2, sort_keys=False))


def _cmd_tree(args) -> int:
    org = _load(args.input)
    if args.format == "json":
        _emit_json(org.to_dict())
    else:
        print(render_tree(org))
    return 0


def _cmd_metrics(args) -> int:
    org = _load(args.input)
    rows = org.to_dict()["employees"]
    if args.format == "json":
        _emit_json(rows)
        return 0
    hdr = f"{'NAME':<24}{'TITLE':<22}{'DEPTH':>6}{'DIRECT':>8}{'TOTAL':>8}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        name = (r["name"][:23])
        title = (r["title"][:21])
        print(f"{name:<24}{title:<22}{r['depth']:>6}{r['direct_reports']:>8}{r['total_reports']:>8}")
    return 0


def _cmd_summary(args) -> int:
    org = _load(args.input)
    s = org.summary()
    if args.format == "json":
        _emit_json(s)
        return 0
    for k, v in s.items():
        label = k.replace("_", " ").title()
        print(f"{label:<26}{v}")
    return 0


def _cmd_validate(args) -> int:
    # parse/build raise OrgError on any structural problem; reaching here is OK.
    org = _load(args.input)
    result = {"valid": True, "headcount": len(org.employees), "roots": list(org.roots)}
    if args.format == "json":
        _emit_json(result)
    else:
        print(f"OK: {result['headcount']} employees, {len(org.roots)} root(s), no structural errors")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=TOOL_NAME, description="Org charts and headcount plans from CSV / HRIS exports.")
    p.add_argument("--version", action="version", version=f"{TOOL_NAME} {TOOL_VERSION}")
    p.add_argument("--format", choices=["table", "json"], default="table", help="output format")
    sub = p.add_subparsers(dest="command", required=True)

    for name, fn, help_ in (
        ("tree", _cmd_tree, "render the reporting tree"),
        ("metrics", _cmd_metrics, "per-employee span-of-control and headcount roll-up"),
        ("summary", _cmd_summary, "org-wide structure summary"),
        ("validate", _cmd_validate, "validate structural integrity"),
    ):
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("input", help="path to CSV file, or - for stdin")
        sp.set_defaults(func=fn)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # propagate global --format default down to subcommand namespace
    if not hasattr(args, "format") or args.format is None:
        args.format = "table"
    try:
        return args.func(args)
    except OrgError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
