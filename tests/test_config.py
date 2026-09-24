"""Tests for the user-level config file."""

import os
import stat
import sys

try:
    from ai_image_renamer import config
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from ai_image_renamer import config

try:
    from tests.base import IsolatedTestCase
except ImportError:
    from base import IsolatedTestCase


class TestConfig(IsolatedTestCase):
    """The editable config lives under the user config directory."""

    def test_config_path_uses_xdg_config_home(self):
        """XDG_CONFIG_HOME selects the directory that holds .env."""
        expected = os.path.join(self._config_tmp.name, "ai-image-renamer-cli", ".env")
        self.assertEqual(config.config_path(), expected)

    def test_config_path_defaults_to_home_config_dir(self):
        """Without XDG_CONFIG_HOME the file is ~/.config/ai-image-renamer-cli/.env."""
        home = os.path.join(self._config_tmp.name, "home")
        os.makedirs(home)
        saved_home = os.environ.get("HOME")
        os.environ.pop("XDG_CONFIG_HOME", None)
        os.environ["HOME"] = home
        try:
            expected = os.path.join(home, ".config", "ai-image-renamer-cli", ".env")
            self.assertEqual(config.config_path(), expected)
        finally:
            if saved_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = saved_home
            os.environ["XDG_CONFIG_HOME"] = self._config_tmp.name

    def test_missing_file_is_created_private(self):
        """First read writes a 0600 template in a 0700 directory."""
        path = config.ensure_config_file()
        self.assertTrue(os.path.isfile(path))
        self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(os.stat(os.path.dirname(path)).st_mode), 0o700)
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("GROQ_API_KEY=", text)
        self.assertIn("DEFAULT_WORD_COUNT=6", text)
        self.assertIn("MODEL=qwen/qwen3.8-27b", text)

    def test_existing_file_is_not_overwritten(self):
        """A second run keeps edits the user made to the config file."""
        path = config.ensure_config_file()
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("DEFAULT_WORD_COUNT=9\nTEMPERATURE=2.0\n")
        config.clear_cache()
        config.ensure_config_file()
        self.assertEqual(config.get("DEFAULT_WORD_COUNT"), "9")
        self.assertEqual(config.get("TEMPERATURE"), "2.0")
        self.assertEqual(config.get("MODEL"), "qwen/qwen3.8-27b")

    def test_dotenv_syntax_and_comments(self):
        """export, quotes, and comments follow .env rules."""
        path = config.config_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(
                "# comment\n"
                "export DEFAULT_WORD_COUNT=\"11\"\n"
                "MODEL='custom/model'\n"
                "\n"
                "GROQ_API_KEY=\n"
            )
        config.clear_cache()
        self.assertEqual(config.get("DEFAULT_WORD_COUNT"), "11")
        self.assertEqual(config.get("MODEL"), "custom/model")
        self.assertEqual(config.get("GROQ_API_KEY"), "")

    def test_working_directory_config_is_ignored(self):
        """A config.ini next to the photos is not the installed app's config."""
        cwd = os.path.join(self._config_tmp.name, "photos")
        os.makedirs(cwd)
        with open(os.path.join(cwd, "config.ini"), "w", encoding="utf-8") as handle:
            handle.write("DEFAULT_WORD_COUNT=2\n")
        previous = os.getcwd()
        os.chdir(cwd)
        try:
            config.clear_cache()
            self.assertEqual(config.get("DEFAULT_WORD_COUNT"), "6")
            self.assertNotEqual(os.path.dirname(config.config_path()), cwd)
        finally:
            os.chdir(previous)

    def test_exported_api_key_overrides_config_file(self):
        """The shell's exported key wins over a different key stored in the file."""
        path = config.config_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("GROQ_API_KEY=from-file\nMODEL=from-file-model\n")
        os.environ["GROQ_API_KEY"] = "from-env"
        config.clear_cache()

        loaded = config.load_environment()

        self.assertEqual(loaded, path)
        self.assertEqual(os.environ["GROQ_API_KEY"], "from-env")
        config.clear_cache()
        self.assertEqual(config.get("GROQ_API_KEY"), "from-env")
        self.assertEqual(config.get("MODEL"), "from-file-model")

    def test_empty_config_value_does_not_wipe_exported_api_key(self):
        """The template's blank GROQ_API_KEY= must not erase an exported key."""
        os.environ["GROQ_API_KEY"] = "from-env"
        config.load_environment()
        self.assertEqual(os.environ["GROQ_API_KEY"], "from-env")
        config.clear_cache()
        self.assertEqual(config.get("GROQ_API_KEY"), "from-env")

    def test_config_file_fills_api_key_when_environment_is_empty(self):
        """A key written in the user config is visible when the shell did not export one."""
        path = config.config_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("GROQ_API_KEY=from-file\n")
        os.environ.pop("GROQ_API_KEY", None)
        config.clear_cache()

        config.load_environment()

        self.assertEqual(os.environ["GROQ_API_KEY"], "from-file")
        config.clear_cache()
        self.assertEqual(config.get("GROQ_API_KEY"), "from-file")
