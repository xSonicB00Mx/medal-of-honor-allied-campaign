"""Small deterministic tests for archive precedence and listing order."""
from pathlib import Path
import tempfile
import unittest
import zipfile
from consolidate_release_packages import effective_members


TEST_ROOT = Path(__file__).resolve().parents[1]/'generated-local/consolidation-unit-tests'
TEST_ROOT.mkdir(parents=True, exist_ok=True)
assert TEST_ROOT.resolve().is_relative_to(Path(__file__).resolve().parents[1])


class ConsolidationTests(unittest.TestCase):
    def test_precedence_case_and_shader_order(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as temp:
            root = Path(temp)
            low, high = root/'zzz_old.pk3', root/'zzzz_patch.pk3'
            with zipfile.ZipFile(low, 'w') as z:
                z.writestr('scripts/z.shader', b'old')
                z.writestr('scripts/a.shader', b'other')
            with zipfile.ZipFile(high, 'w') as z:
                z.writestr('SCRIPTS/Z.shader', b'new')
                z.writestr('scripts/m.shader', b'new material')
            result = effective_members([high, low])
            self.assertEqual(list(result), ['scripts/z.shader', 'scripts/m.shader', 'scripts/a.shader'])
            self.assertEqual(result['scripts/z.shader'][0], b'new')

    def test_duplicate_inside_package_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as temp:
            path = Path(temp)/'bad.pk3'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('a.txt', b'a')
                z.writestr('A.txt', b'b')
            with self.assertRaises(AssertionError):
                effective_members([path])

    def test_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as temp:
            path = Path(temp)/'bad.pk3'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('../a.txt', b'a')
            with self.assertRaises(AssertionError):
                effective_members([path])


if __name__ == '__main__':
    unittest.main()
