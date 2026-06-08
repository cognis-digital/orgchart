import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orgchart import TOOL_NAME, TOOL_VERSION, parse_csv, build_org, render_tree
from orgchart.core import OrgError
from orgchart.cli import main, build_parser


CSV = (
    "id,name,title,manager_id,salary\n"
    "1,Dana,CEO,,400000\n"
    "2,Marcus,VP Eng,1,290000\n"
    "3,Priya,VP People,1,260000\n"
    "4,Sam,Eng Manager,2,200000\n"
    "5,Tom,Engineer,4,160000\n"
)


class TestParse(unittest.TestCase):
    def test_parse_and_aliases(self):
        emps = parse_csv("employee_id,full_name,reports_to,base_salary\n7,Jo,,100000\n")
        self.assertEqual(len(emps), 1)
        self.assertEqual(emps[0].id, "7")
        self.assertEqual(emps[0].name, "Jo")
        self.assertIsNone(emps[0].manager_id)
        self.assertEqual(emps[0].salary, 100000.0)

    def test_missing_id_column(self):
        with self.assertRaises(OrgError):
            parse_csv("name,title\nDana,CEO\n")

    def test_duplicate_id(self):
        with self.assertRaises(OrgError):
            parse_csv("id,name\n1,A\n1,B\n")

    def test_bad_salary(self):
        with self.assertRaises(OrgError):
            parse_csv("id,name,salary\n1,A,abc\n")


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.org = build_org(parse_csv(CSV))

    def test_root(self):
        self.assertEqual(self.org.roots, ["1"])

    def test_direct_and_total_reports(self):
        self.assertEqual(self.org.direct_reports("1"), 2)  # Marcus, Priya
        self.assertEqual(self.org.total_reports("1"), 4)   # all but the CEO
        self.assertEqual(self.org.total_reports("2"), 2)   # Sam + Tom
        self.assertEqual(self.org.direct_reports("5"), 0)

    def test_depth(self):
        self.assertEqual(self.org.depth("1"), 0)
        self.assertEqual(self.org.depth("2"), 1)
        self.assertEqual(self.org.depth("4"), 2)
        self.assertEqual(self.org.depth("5"), 3)

    def test_summary(self):
        s = self.org.summary()
        self.assertEqual(s["headcount"], 5)
        self.assertEqual(s["max_depth"], 3)
        self.assertEqual(s["total_salary"], 1310000.0)
        self.assertEqual(s["max_span_of_control"], 2)

    def test_unknown_manager(self):
        with self.assertRaises(OrgError):
            build_org(parse_csv("id,name,manager_id\n1,A,99\n"))

    def test_self_reference(self):
        with self.assertRaises(OrgError):
            build_org(parse_csv("id,name,manager_id\n1,A,1\n"))

    def test_cycle(self):
        # 1->2->1 with no root: every row has a manager
        with self.assertRaises(OrgError):
            build_org(parse_csv("id,name,manager_id\n1,A,2\n2,B,1\n"))

    def test_render_tree(self):
        out = render_tree(self.org)
        self.assertIn("Dana", out)
        self.assertIn("Tom", out)
        # CEO line should show total roll-up
        self.assertIn("[4 reports]", out)


class TestCli(unittest.TestCase):
    def _run(self, argv):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            code = main(argv)
        finally:
            sys.stdout = old
        return code, buf.getvalue()

    def _write(self, text):
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        self.addCleanup(os.remove, path)
        return path

    def test_version(self):
        self.assertTrue(TOOL_NAME)
        self.assertTrue(TOOL_VERSION)
        self.assertIsNotNone(build_parser())

    def test_summary_json(self):
        path = self._write(CSV)
        code, out = self._run(["--format", "json", "summary", path])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["headcount"], 5)
        self.assertEqual(data["roots"], ["1"])

    def test_tree_json(self):
        path = self._write(CSV)
        code, out = self._run(["--format", "json", "tree", path])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(len(data["employees"]), 5)

    def test_metrics_table(self):
        path = self._write(CSV)
        code, out = self._run(["metrics", path])
        self.assertEqual(code, 0)
        self.assertIn("DIRECT", out)
        self.assertIn("Dana", out)

    def test_validate_ok(self):
        path = self._write(CSV)
        code, _ = self._run(["validate", path])
        self.assertEqual(code, 0)

    def test_validate_failure_nonzero(self):
        path = self._write("id,name,manager_id\n1,A,99\n")
        # error goes to stderr; capture is unnecessary, we only need exit code
        code = main(["validate", path])
        self.assertEqual(code, 1)

    def test_missing_file_nonzero(self):
        code = main(["summary", "/nonexistent/path/does/not/exist.csv"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
