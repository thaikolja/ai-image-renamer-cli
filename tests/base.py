"""Keep tests away from the real user config and shell secrets."""

import os
import sys
import tempfile
import unittest

_ENV_KEYS = ("XDG_CONFIG_HOME", "GROQ_API_KEY", "GROQ_MODEL", "OPENAI_API_KEY")


def _config_module():
    """Import the config module from the source tree when it is not installed."""
    try:
        from ai_image_renamer import config
    except ImportError:
        src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        if src not in sys.path:
            sys.path.insert(0, src)
        from ai_image_renamer import config
    return config


class IsolatedTestCase(unittest.TestCase):
    """Point config reads at a temporary XDG directory for one test."""

    def setUp(self):
        """Redirect the user config directory and hide real API keys."""
        super().setUp()
        self._config_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._config_tmp.cleanup)
        self._saved_env = {key: os.environ.get(key) for key in _ENV_KEYS}
        os.environ["XDG_CONFIG_HOME"] = self._config_tmp.name
        for key in _ENV_KEYS:
            if key != "XDG_CONFIG_HOME":
                os.environ.pop(key, None)
        _config_module().clear_cache()
        self.addCleanup(self._restore_env)

    def _restore_env(self):
        """Put the process environment back and drop the config cache."""
        for key, value in self._saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        _config_module().clear_cache()
