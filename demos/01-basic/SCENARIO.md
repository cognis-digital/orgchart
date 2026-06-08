# Demo 01 - Basic org chart from an HRIS export

A people-ops analyst exports the company roster from the HRIS as a flat
CSV (`roster.csv`). Each row is one employee and points at their manager
via `manager_id`. The CEO has no manager.

The analyst wants three things before a reorg planning meeting:

1. A readable reporting tree.
2. Span-of-control / depth / total-headcount per leader.
3. A one-shot org summary (headcount, avg span, max depth, total comp).

## Run it

```sh
# Reporting tree
python -m orgchart tree demos/01-basic/roster.csv

# Per-employee metrics table
python -m orgchart metrics demos/01-basic/roster.csv

# Org-wide summary as JSON (good for piping into a dashboard)
python -m orgchart --format json summary demos/01-basic/roster.csv

# CI gate: fail the build if the export has a broken reporting structure
python -m orgchart validate demos/01-basic/roster.csv
```

## What to expect

`tree` prints an indented chart rooted at the CEO. `metrics` shows that
the VPs carry larger `total_reports` than their `direct_reports` because
the roll-up counts their whole sub-org. `summary` reports an average
span-of-control around 2 and a max depth of 3.

## Header flexibility

The parser accepts common HRIS aliases, so `employee_id`/`emp_id`,
`full_name`/`employee_name`, `reports_to`/`manager`, and `base_salary`
all work without remapping the file by hand.
