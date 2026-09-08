import json
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


if __name__ == '__main__':
    unittest.main()
