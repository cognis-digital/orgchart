"""ORGCHART - org charts and headcount plans from CSV / HRIS exports.

Standard-library-only toolkit for ops and people teams. Reads a flat
employee CSV (one row per person, pointing at a manager), validates the
reporting structure, and produces:

  * a rendered org tree
  * span-of-control and depth metrics per manager
  * a headcount roll-up (direct + total reports) per node
  * detection of structural problems (cycles, missing managers, orphans)

No third-party dependencies, no network access.
"""

from .core import (
    Employee,
    OrgChart,
    OrgError,
    parse_csv,
    build_org,
    render_tree,
)

TOOL_NAME = "orgchart"
TOOL_VERSION = "1.0.0"

__all__ = [
    "Employee",
    "OrgChart",
    "OrgError",
    "parse_csv",
    "build_org",
    "render_tree",
    "TOOL_NAME",
    "TOOL_VERSION",
]
