import subprocess
import sys
import unittest


class TestAutoInstall(unittest.TestCase):
    def test_ensure_dependencies_can_be_imported(self) -> None:
        """Test that the _ensure_deps module can be imported."""
        from autoflight._ensure_deps import ensure_dependencies
        # Should not raise any errors
        ensure_dependencies()
    
    def test_module_import_triggers_auto_install(self) -> None:
        """Test that importing autoflight triggers dependency check."""
        # Run in a subprocess to test fresh import
        result = subprocess.run(
            [sys.executable, "-c", "import autoflight"],
            capture_output=True,
            text=True,
        )
        # Should succeed regardless of whether deps were already installed
        self.assertEqual(result.returncode, 0)
    
    def test_orthomosaic_module_can_be_run(self) -> None:
        """Test that the orthomosaic module can be run with --help."""
        result = subprocess.run(
            [sys.executable, "-m", "autoflight.orthomosaic", "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)
