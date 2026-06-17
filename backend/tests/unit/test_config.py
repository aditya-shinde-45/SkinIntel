import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


CONFIG_FILE = Path(__file__).resolve().parents[2] / "app" / "config.py"
CONFIG_SPEC = importlib.util.spec_from_file_location("config_under_test", CONFIG_FILE)
config_module = importlib.util.module_from_spec(CONFIG_SPEC)
assert CONFIG_SPEC.loader is not None
CONFIG_SPEC.loader.exec_module(config_module)


class ConfigPathResolutionTests(unittest.TestCase):
    def test_prefers_existing_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "skin_concern_model.keras"
            model_path.write_text("placeholder")

            self.assertEqual(config_module._resolve_existing_path(str(model_path)), str(model_path))

    def test_falls_back_to_app_models_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            app_root = Path(tmpdir)
            model_path = app_root / "models" / "skin_concern_model.keras"
            model_path.parent.mkdir(parents=True)
            model_path.write_text("placeholder")

            fake_config_path = app_root / "backend" / "app" / "config.py"
            fake_config_path.parent.mkdir(parents=True)
            fake_config_path.write_text("placeholder")

            with mock.patch.object(config_module, "__file__", str(fake_config_path)):
                resolved = config_module._resolve_existing_path("/missing/skin_concern_model.keras")

            self.assertEqual(resolved, str(model_path))


if __name__ == "__main__":
    unittest.main()