"""Core org-chart engine.

The input model is the standard HRIS export shape: a flat list of
employees, each carrying a unique id, a name, a title, an optional
manager_id, and an optional salary. The engine assembles that into a
reporting tree, validates it, and computes the headcount / span-of-control
metrics that ops + people teams actually need for planning.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class OrgError(Exception):
    """Raised on malformed input or an unbuildable reporting structure."""


# Accepted header aliases -> canonical field name. HRIS exports vary wildly.
_FIELD_ALIASES = {
    "id": "id",
    "employee_id": "id",
    "emp_id": "id",
    "name": "name",
    "employee_name": "name",
    "full_name": "name",
    "title": "title",
    "job_title": "title",
    "role": "title",
    "manager_id": "manager_id",
    "manager": "manager_id",
    "reports_to": "manager_id",
    "salary": "salary",
    "base_salary": "salary",
    "comp": "salary",
}


@dataclass
class Employee:
    id: str
    name: str
    title: str = ""
    manager_id: Optional[str] = None
    salary: float = 0.0
    # Filled in during build:
    reports: List[str] = field(default_factory=list)


@dataclass
class OrgChart:
    employees: Dict[str, Employee]
    roots: List[str]

    # --- metrics -------------------------------------------------------

    def direct_reports(self, emp_id: str) -> int:
        return len(self.employees[emp_id].reports)

    def total_reports(self, emp_id: str) -> int:
        """All descendants (the full sub-org), excluding the node itself."""
        seen = 0
        stack = list(self.employees[emp_id].reports)
        while stack:
            cur = stack.pop()
            seen += 1
            stack.extend(self.employees[cur].reports)
        return seen

    def depth(self, emp_id: str) -> int:
        """Distance from the top of this employee's tree (root = 0)."""
        d = 0
        cur = self.employees[emp_id].manager_id
        while cur is not None:
            d += 1
            cur = self.employees[cur].manager_id
        return d

    def managers(self) -> List[str]:
        return [e.id for e in self.employees.values() if e.reports]

    def max_depth(self) -> int:
        return max((self.depth(e) for e in self.employees), default=0)

    def summary(self) -> dict:
        mgr_ids = self.managers()
        spans = [self.direct_reports(m) for m in mgr_ids]
        ics = [e.id for e in self.employees.values() if not e.reports]
        total_salary = sum(e.salary for e in self.employees.values())
        return {
            "headcount": len(self.employees),
            "managers": len(mgr_ids),
            "individual_contributors": len(ics),
            "roots": list(self.roots),
            "max_depth": self.max_depth(),
            "avg_span_of_control": round(sum(spans) / len(spans), 2) if spans else 0.0,
            "max_span_of_control": max(spans, default=0),
            "total_salary": round(total_salary, 2),
        }

    def to_dict(self) -> dict:
        people = []
        for e in sorted(self.employees.values(), key=lambda x: (self.depth(x.id), x.name)):
            people.append(
                {
                    "id": e.id,
                    "name": e.name,
                    "title": e.title,
                    "manager_id": e.manager_id,
                    "salary": e.salary,
                    "depth": self.depth(e.id),
                    "direct_reports": self.direct_reports(e.id),
                    "total_reports": self.total_reports(e.id),
                }
            )
        return {"summary": self.summary(), "employees": people}


def _normalize_headers(fieldnames: List[str]) -> Dict[str, str]:
    """Map raw CSV headers to canonical fields, case/space-insensitive."""
    mapping: Dict[str, str] = {}
    for raw in fieldnames or []:
        key = raw.strip().lower().replace(" ", "_")
        if key in _FIELD_ALIASES:
            mapping[raw] = _FIELD_ALIASES[key]
    return mapping


def parse_csv(text: str) -> List[Employee]:
    """Parse an HRIS-style CSV string into Employee records."""
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise OrgError("empty input: no CSV header found")
    mapping = _normalize_headers(reader.fieldnames)
    canon = set(mapping.values())
    if "id" not in canon:
        raise OrgError("CSV must have an id column (id/employee_id/emp_id)")
    if "name" not in canon:
        raise OrgError("CSV must have a name column (name/employee_name/full_name)")

    employees: List[Employee] = []
    seen_ids = set()
    for lineno, row in enumerate(reader, start=2):
        rec: Dict[str, str] = {}
        for raw, value in row.items():
            if raw in mapping:
                rec[mapping[raw]] = (value or "").strip()
        emp_id = rec.get("id", "")
        if not emp_id:
            raise OrgError(f"line {lineno}: missing employee id")
        if emp_id in seen_ids:
            raise OrgError(f"line {lineno}: duplicate employee id {emp_id!r}")
        seen_ids.add(emp_id)
        name = rec.get("name", "")
        if not name:
            raise OrgError(f"line {lineno}: employee {emp_id!r} missing name")
        mgr = rec.get("manager_id") or None
        salary_raw = rec.get("salary", "")
        try:
            salary = float(salary_raw.replace(",", "").replace("$", "")) if salary_raw else 0.0
        except ValueError:
            raise OrgError(f"line {lineno}: bad salary {salary_raw!r} for {emp_id!r}")
        employees.append(
            Employee(id=emp_id, name=name, title=rec.get("title", ""), manager_id=mgr, salary=salary)
        )
    if not employees:
        raise OrgError("no employee rows found")
    return employees


def build_org(employees: List[Employee]) -> OrgChart:
    """Assemble + validate a reporting tree. Raises OrgError on bad structure."""
    by_id: Dict[str, Employee] = {}
    for e in employees:
        # defensive copy so callers' reports lists aren't mutated/shared
        by_id[e.id] = Employee(id=e.id, name=e.name, title=e.title,
                               manager_id=e.manager_id, salary=e.salary)

    roots: List[str] = []
    for e in by_id.values():
        if e.manager_id is None:
            roots.append(e.id)
            continue
        if e.manager_id == e.id:
            raise OrgError(f"employee {e.id!r} reports to themselves")
        mgr = by_id.get(e.manager_id)
        if mgr is None:
            raise OrgError(
                f"employee {e.id!r} reports to unknown manager {e.manager_id!r}"
            )
        mgr.reports.append(e.id)

    # stable ordering of reports for deterministic output
    for e in by_id.values():
        e.reports.sort(key=lambda cid: (by_id[cid].name, cid))

    if not roots:
        raise OrgError("no top-level employee found (cycle or every row has a manager)")

    # cycle detection: every node must be reachable from a root
    reachable = set()
    stack = list(roots)
    while stack:
        cur = stack.pop()
        if cur in reachable:
            continue
        reachable.add(cur)
        stack.extend(by_id[cur].reports)
    if len(reachable) != len(by_id):
        stranded = sorted(set(by_id) - reachable)
        raise OrgError(
            "reporting cycle detected; employees not reachable from a root: "
            + ", ".join(stranded)
        )

    roots.sort(key=lambda rid: (by_id[rid].name, rid))
    return OrgChart(employees=by_id, roots=roots)


def render_tree(org: OrgChart) -> str:
    """Render the org as an indented ASCII tree."""
    lines: List[str] = []

    def walk(emp_id: str, prefix: str, is_last: bool, is_root: bool) -> None:
        e = org.employees[emp_id]
        connector = "" if is_root else ("└─ " if is_last else "├─ ")
        label = e.name
        if e.title:
            label += f" ({e.title})"
        if e.reports:
            label += f"  [{org.total_reports(emp_id)} reports]"
        lines.append(prefix + connector + label)
        child_prefix = prefix + ("" if is_root else ("   " if is_last else "│  "))
        kids = e.reports
        for i, c in enumerate(kids):
            walk(c, child_prefix, i == len(kids) - 1, False)

    for r in org.roots:
        walk(r, "", True, True)
    return "\n".join(lines)


def load_org_from_csv(text: str) -> OrgChart:
    return build_org(parse_csv(text))
