import tempfile
import unittest
from pathlib import Path
from devpulse import audit_plugin_ast, PluginSecurityError, load_plugins


class TestDevPulseSecurity(unittest.TestCase):
    def test_blocks_unsafe_eval(self):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
            tmp.write("def run(args):\n    eval('1+1')\n")
            tmp_path = Path(tmp.name)

        try:
            with self.assertRaises(PluginSecurityError):
                audit_plugin_ast(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_blocks_subprocess_shell_true(self):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
            tmp.write("import subprocess\ndef run(args):\n    subprocess.run('ls', shell=True)\n")
            tmp_path = Path(tmp.name)

        try:
            with self.assertRaises(PluginSecurityError):
                audit_plugin_ast(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_loads_all_builtin_plugins_cleanly(self):
        plugins = load_plugins(strict_security=True)
        expected = {"port_audit", "git_health", "net_diag", "env_guard", "sys_pulse"}
        self.assertTrue(expected.issubset(set(plugins.keys())))


if __name__ == "__main__":
    unittest.main()