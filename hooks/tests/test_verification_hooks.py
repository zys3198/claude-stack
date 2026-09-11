import json
import runpy
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import unittest


HOOKS = Path(__file__).resolve().parents[1]


class VerificationHookTests(unittest.TestCase):
    def test_retired_guards_are_absent_and_unregistered(self):
        settings = json.loads((HOOKS.parent / 'settings.json').read_text(encoding='utf-8'))
        commands = [hook.get('command', '') for groups in settings.get('hooks', {}).values()
                    for group in groups for hook in group.get('hooks', [])]
        for name in ['git_guard.py', 'secret_guard.py', 'verify_recorder.py']:
            with self.subTest(name=name):
                self.assertFalse((HOOKS / name).exists())
                self.assertFalse(any(name in command for command in commands))

    def test_current_snapshot_is_not_reported_as_degraded(self):
        guard = runpy.run_path(str(HOOKS / 'settings-degrade-guard.py'))
        output = StringIO()
        with redirect_stdout(output):
            guard['main']()
        self.assertEqual(output.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
