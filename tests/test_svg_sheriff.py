import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from svg_sheriff import audit_svg

class AuditTests(unittest.TestCase):
    def test_clean_svg(self):
        self.assertEqual([],audit_svg('<svg viewBox="0 0 10 10"><title>Dot</title><circle r="2"/></svg>'))
    def test_missing_accessible_name(self):
        self.assertIn("A11Y001",{x.rule for x in audit_svg('<svg viewBox="0 0 1 1"/>')})
    def test_animation_warns(self):
        self.assertIn("MOTION001",{x.rule for x in audit_svg('<svg viewBox="0 0 1 1"><title>x</title><animate attributeName="x"/></svg>')})
    def test_script_is_error(self):
        self.assertIn("SEC001",{x.rule for x in audit_svg('<svg><title>x</title><script>alert(1)</script></svg>')})
    def test_event_handler_is_error(self):
        self.assertIn("SEC002",{x.rule for x in audit_svg('<svg><title>x</title><rect onclick="x()"/></svg>')})
    def test_invalid_xml(self):
        self.assertEqual("SVG001",audit_svg("<svg>")[0].rule)

if __name__=="__main__": unittest.main()
