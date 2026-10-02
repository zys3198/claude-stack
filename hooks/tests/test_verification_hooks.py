import json
from pathlib import Path
import unittest


HOOKS = Path(__file__).resolve().parents[1]
SETTINGS = HOOKS.parent / 'settings.json'


def registered_commands():
    settings = json.loads(SETTINGS.read_text(encoding='utf-8'))
    return [hook.get('command', '') for groups in settings.get('hooks', {}).values()
            for group in groups for hook in group.get('hooks', [])]


class VerificationHookTests(unittest.TestCase):
    def test_retired_guards_are_absent_and_unregistered(self):
        commands = registered_commands()
        for name in ['git_guard.py', 'secret_guard.py', 'verify_recorder.py']:
            with self.subTest(name=name):
                self.assertFalse((HOOKS / name).exists())
                self.assertFalse(any(name in command for command in commands))

    def test_settings_degrade_guard_is_retired(self):
        # settings-degrade-guard.py 已归档退役：SessionStart 那个位置由
        # scripts/session-guard.py 接任（见 installing/custom-setup.md 台账核实条目）。
        # 本用例原先 run_path 加载它并断言「不报降级」，脚本删除后必然 FileNotFoundError。
        # 退役守卫的判据与上一条同构：文件不在磁盘，且没有任何 settings 注册还指向它。
        name = 'settings-degrade-guard.py'
        self.assertFalse((HOOKS / name).exists())
        self.assertFalse(any(name in command for command in registered_commands()))

    def test_session_guard_replaced_settings_degrade_guard(self):
        # 退役不能留空档：确认 SessionStart 仍由 session-guard.py 承担。
        settings = json.loads(SETTINGS.read_text(encoding='utf-8'))
        start = settings.get('hooks', {}).get('SessionStart', [])
        commands = [hook.get('command', '') for group in start for hook in group.get('hooks', [])]
        self.assertTrue(any('session-guard.py' in command for command in commands))


if __name__ == '__main__':
    unittest.main()
