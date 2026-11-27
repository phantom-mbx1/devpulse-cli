import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from devpulse import build_parser, load_plugins


class TestCacheAudit(unittest.TestCase):
    def test_reports_cache_bytes_without_counting_nested_directories_twice(self):
        plugins = load_plugins(strict_security=True)
        assert "cache_audit" in plugins, "cache_audit should be available as a CLI command"

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "project"
            for relative_path, size in {
                "src/__pycache__/app.pyc": 3,
                "src/.pytest_cache/state": 5,
                "src/node_modules/package/index.js": 7,
                "src/node_modules/package/dist/bundle.js": 11,
                "src/node_modules/package/dist/nested/dist/map.js": 13,
                "other/dist/main.js": 17,
                "src/ordinary.txt": 100,
            }.items():
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"x" * size)

            outside = Path(temporary) / "outside"
            outside.mkdir()
            outside_file = outside / "outside.bin"
            outside_file.write_bytes(b"x" * 100)
            try:
                (root / "src/__pycache__/linked.bin").symlink_to(outside_file)
                (root / "src/node_modules/linked").symlink_to(outside, target_is_directory=True)
            except (NotImplementedError, OSError):
                # Some Windows setups do not grant permission to create links.
                pass

            args = build_parser(plugins).parse_args(["cache_audit", "--path", str(root)])
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(plugins[args.command].run(args), 0)

        lines = output.getvalue().splitlines()
        for cache, size in {
            "__pycache__": 3,
            ".pytest_cache": 5,
            "node_modules": 7,
            "dist": 41,
            "Total": 56,
        }.items():
            self.assertIn(f"{cache}: {size} bytes", lines)
