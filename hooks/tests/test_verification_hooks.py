import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HOOKS = Path(__file__).resolve().parents[1]


class VerificationHookTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_path = Path(self.temp_dir.name) / "edited_state.json"
        self.write_state({
            "session_id": "session-1",
            "paths": ["feature.py"],
            "edits_per_path": {"feature.py": 1},
            "last_edit_ts": 1.0,
            "last_verify_ts": 0.0,
            "verify_cmds": [],
            "stop_blocks": 0,
            "code_pending": ["feature.py"],
        })

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_git_guard_binds_confirmation_to_operation(self):
        cases = [
            ("git commit -m change", "确认第一批修改", False),
            ("git commit -m change", "确认推送", False),
            ("git commit -m change", "确认不要提交", False),
            ("git commit -m change", "确认不提交", False),
            ("git commit -m change", "确认别提交", False),
            ("git commit -m change", "确认勿提交", False),
            ("git commit -m change", "confirm no commit", False),
            ("git commit -m change", "confirm avoid commit", False),
            ("git commit -m change", "确认提交", True),
            ("git commit -m \"mention git push\"", "确认提交", True),
            ("git commit -m change && git push origin main", "确认提交并推送", False),
            ("git commit -m change && git commit -m again", "确认提交", False),
            ("git push origin main", "确认提交", False),
            ("git push origin main", "确认推送", True),
            ("git push origin main", "确认不推送", False),
            ("git push origin main", "确认不要推送", False),
            ("git push origin main", "确认别推送", False),
            ("git push origin main", "确认勿推送", False),
            ("git push origin main", "confirm no push", False),
            ("git push origin main", "confirm avoid push", False),
            ("git push origin main && git push origin backup", "确认推送", False),
            ("git push origin main", "确认不要提交，但确认推送", True),
            ("git switch -c feature", "确认创建分支", True),
            ("git switch -c feature", "确认不创建分支", False),
            ("git switch -c feature", "确认不要创建分支", False),
            ("git switch -c feature", "确认别创建分支", False),
            ("git switch -c feature", "确认勿创建分支", False),
            ("git switch -c feature", "confirm no branch", False),
            ("git switch -c feature", "confirm avoid branch", False),
            ("git checkout -b feature && git checkout -b feature2", "确认创建分支", False),
        ]
        for command, prompt, allowed in cases:
            result = self.run_git_guard(command, prompt)
            self.assertEqual(result.returncode, 0)
            if allowed:
                self.assertEqual(result.stdout, "")
            else:
                payload = json.loads(result.stdout)
                output = payload["hookSpecificOutput"]
                self.assertEqual(output["permissionDecision"], "deny")

    def test_git_guard_log_redacts_command(self):
        command = 'git commit -m "token-value-123"'
        result = self.run_git_guard(command, "确认提交")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        log = (Path(self.temp_dir.name) / "git_guard.log").read_text(encoding="utf-8")
        self.assertNotIn(command, log)
        self.assertNotIn("token-value-123", log)
        self.assertIn("cmd_sha256=", log)
        self.assertIn("cmd_len=", log)

    def test_git_guard_parse_error_log_redacts_input(self):
        raw = '{"tool_input": {"command": "token-value-123"}'
        log_path = Path(self.temp_dir.name) / "git_guard.log"
        env = os.environ.copy()
        env["CLAUDE_GIT_GUARD_LOG"] = str(log_path)
        result = subprocess.run(
            [sys.executable, str(HOOKS / "git_guard.py")],
            input=raw,
            text=True,
            encoding="utf-8",
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        log = log_path.read_text(encoding="utf-8")
        self.assertNotIn(raw, log)
        self.assertNotIn("token-value-123", log)
        self.assertIn("raw_sha256=", log)
        self.assertIn("raw_len=", log)

    def test_successful_verification_accepts_current_bash_response(self):
        success = self.run_hook("verify_recorder.py", self.recorder_event({
            "stdout": "1 passed",
            "stderr": "",
            "interrupted": False,
            "isImage": False,
            "noOutputExpected": False,
            "dangerouslyDisableSandbox": False,
        }))
        self.assertEqual(success.returncode, 0)
        state = self.read_state()
        self.assertEqual(state["verify_cmds"], ["python.exe -m unittest"])
        self.assertGreater(state["last_verify_ts"], state["last_edit_ts"])

    def write_state(self, state):
        self.state_path.write_text(json.dumps(state), encoding="utf-8")

    def read_state(self):
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def run_hook(self, script, event):
        env = os.environ.copy()
        env["CLAUDE_HOOK_STATE"] = str(self.state_path)
        return subprocess.run(
            [sys.executable, str(HOOKS / script)],
            input=json.dumps(event),
            text=True,
            encoding="utf-8",
            capture_output=True,
            env=env,
            check=False,
        )

    def run_git_guard(self, command, prompt):
        transcript = Path(self.temp_dir.name) / "transcript.jsonl"
        transcript.write_text(
            json.dumps({"type": "user", "message": {"content": prompt}}) + "\n",
            encoding="utf-8",
        )
        event = {
            "hook_event_name": "PreToolUse",
            "session_id": "session-1",
            "tool_name": "Bash",
            "tool_input": {"command": command},
            "transcript_path": str(transcript),
        }
        env = os.environ.copy()
        env["CLAUDE_GIT_GUARD_LOG"] = str(Path(self.temp_dir.name) / "git_guard.log")
        return subprocess.run(
            [sys.executable, str(HOOKS / "git_guard.py")],
            input=json.dumps(event),
            text=True,
            encoding="utf-8",
            capture_output=True,
            env=env,
            check=False,
        )

    def recorder_event(self, response, command="python.exe -m unittest", cwd=None):
        event = {
            "hook_event_name": "PostToolUse",
            "session_id": "session-1",
            "tool_name": "Bash",
            "tool_input": {"command": command},
            "tool_response": response,
        }
        if cwd:
            event["cwd"] = str(cwd)
        return event

    def gate_event(self):
        return {
            "hook_event_name": "Stop",
            "session_id": "session-1",
        }

    def test_failed_verification_does_not_arm_gate_as_success(self):
        failed = self.run_hook("verify_recorder.py", self.recorder_event({
            "stdout": "",
            "stderr": "1 failed",
            "is_error": True,
            "interrupted": False,
        }))
        self.assertEqual(failed.returncode, 0)
        state = self.read_state()
        self.assertEqual(state["verify_cmds"], [])
        self.assertEqual(state["last_verify_ts"], 0.0)

        warning = self.run_hook("verify_gate.py", self.gate_event())
        self.assertEqual(warning.returncode, 0)
        self.assertIn("verify_gate WARNING", warning.stderr)

    def test_unmarked_failure_response_does_not_record_verification(self):
        result = self.run_hook(
            "verify_recorder.py",
            self.recorder_event(
                {
                    "stdout": "",
                    "stderr": "command failed",
                    "interrupted": False,
                }
            ),
        )
        self.assertEqual(result.returncode, 0)
        state = self.read_state()
        self.assertEqual(state["verify_cmds"], [])
        self.assertEqual(state["last_verify_ts"], 0.0)

        state = self.read_state()

    def test_session_mismatch_does_not_reset_pending_state(self):
        state = self.read_state()
        state["session_id"] = "other-session"
        self.write_state(state)

        result = self.run_hook("verify_recorder.py", self.recorder_event({
            "stdout": "1 passed",
            "stderr": "",
            "is_error": False,
            "interrupted": False,
        }))
        self.assertEqual(result.returncode, 0)
        state = self.read_state()
        self.assertEqual(state["session_id"], "other-session")
        self.assertEqual(state["code_pending"], ["feature.py"])
        self.assertEqual(state["verify_cmds"], [])

        blocked = self.run_hook("verify_gate.py", self.gate_event())
        self.assertEqual(blocked.returncode, 2)
        self.assertIn('"decision": "block"', blocked.stdout)

    def test_successful_verification_releases_gate(self):
        success = self.run_hook("verify_recorder.py", self.recorder_event({
            "stdout": "1 passed",
            "stderr": "",
            "is_error": False,
            "interrupted": False,
        }))
        self.assertEqual(success.returncode, 0)
        state = self.read_state()
        self.assertEqual(state["verify_cmds"], ["python.exe -m unittest"])
        self.assertGreater(state["last_verify_ts"], state["last_edit_ts"])

        released = self.run_hook("verify_gate.py", self.gate_event())
        self.assertEqual(released.returncode, 0)
        self.assertEqual(self.read_state()["code_pending"], [])

    def test_gate_warns_after_repeated_unverified_stops(self):
        results = [self.run_hook("verify_gate.py", self.gate_event()) for _ in range(3)]
        self.assertTrue(all(result.returncode == 0 for result in results))
        self.assertTrue(all("verify_gate WARNING" in result.stderr for result in results))
        self.assertTrue(all(result.stdout == "" for result in results))
        self.assertEqual(self.read_state()["code_pending"], ["feature.py"])

    def test_gate_blocks_after_max_unverified_stops(self):
        for _ in range(3):
            warning = self.run_hook("verify_gate.py", self.gate_event())
            self.assertEqual(warning.returncode, 0)
            self.assertIn("verify_gate WARNING", warning.stderr)

        blocked = self.run_hook("verify_gate.py", self.gate_event())
        self.assertEqual(blocked.returncode, 2)
        payload = json.loads(blocked.stdout)
        self.assertEqual(payload["decision"], "block")
        self.assertIn("未跑成功验证", payload["reason"])
        self.assertEqual(self.read_state()["stop_blocks"], 3)

        success = self.run_hook("verify_recorder.py", self.recorder_event({
            "stdout": "1 passed",
            "stderr": "",
            "is_error": False,
            "interrupted": False,
        }))
        self.assertEqual(success.returncode, 0)

        released = self.run_hook("verify_gate.py", self.gate_event())
        self.assertEqual(released.returncode, 0)
        self.assertEqual(self.read_state()["code_pending"], [])

    def test_unknown_or_failed_response_does_not_record_verification(self):
        responses = [
            {"stdout": "looks green", "stderr": ""},
            {"stdout": "failed", "stderr": "", "exit_code": 1},
        ]
        for response in responses:
            result = self.run_hook("verify_recorder.py", self.recorder_event(response))
            self.assertEqual(result.returncode, 0)
        state = self.read_state()
        self.assertEqual(state["verify_cmds"], [])
        self.assertEqual(state["last_verify_ts"], 0.0)

    def test_invalid_state_is_not_overwritten(self):
        self.state_path.write_text("{invalid", encoding="utf-8")
        result = self.run_hook(
            "verify_recorder.py",
            self.recorder_event(
                {
                    "stdout": "1 passed",
                    "stderr": "",
                    "interrupted": False,
                }
            ),
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.state_path.read_text(encoding="utf-8"), "{invalid")

    def test_output_text_does_not_count_as_verification_command(self):
        commands = (
            "echo pytest",
            "python -c \"print('pytest')\"",
            "grep pytest result.log",
            "node -e \"process.exit(0)\"",
        )
        for command in commands:
            result = self.run_hook(
                "verify_recorder.py",
                self.recorder_event(
                    {"stdout": "ok", "stderr": "", "is_error": False},
                    command=command,
                ),
            )
            self.assertEqual(result.returncode, 0)
        self.assertEqual(self.read_state()["verify_cmds"], [])

    def test_stop_hook_active_warns_without_verification(self):
        event = self.gate_event()
        event["stop_hook_active"] = True
        warning = self.run_hook("verify_gate.py", event)
        self.assertEqual(warning.returncode, 0)
        self.assertIn("verify_gate WARNING", warning.stderr)

    def test_gate_detects_shell_code_change(self):
        repo = Path(self.temp_dir.name) / "repo"
        repo.mkdir()
        try:
            initialized = subprocess.run(
                ["git", "init"],
                cwd=repo,
                capture_output=True,
                encoding="utf-8",
                check=False,
            )
        except FileNotFoundError:
            self.skipTest("git unavailable")
        if initialized.returncode != 0:
            self.skipTest("git init unavailable")
        code_path = repo / "feature.py"
        code_path.write_text("value = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "feature.py"], cwd=repo, check=True)
        baseline_hash = __import__("hashlib").sha256(code_path.read_bytes()).hexdigest()
        state = self.read_state()
        state["project_root"] = str(repo)
        state["verified_code_hashes"] = {"feature.py": baseline_hash}
        self.write_state(state)
        code_path.write_text("value = 2\n", encoding="utf-8")

        warning = self.run_hook("verify_gate.py", {**self.gate_event(), "cwd": str(repo)})
        self.assertEqual(warning.returncode, 0)
        self.assertIn("feature.py", warning.stderr)

    def test_secret_guard_blocks_secret_file_and_warns_on_secret_output(self):
        blocked = self.run_hook("secret_guard.py", {
            "hook_event_name": "PreToolUse",
            "session_id": "session-1",
            "tool_name": "Bash",
            "tool_input": {"command": "Get-Content .env"},
        })
        self.assertEqual(blocked.returncode, 0)
        self.assertIn('"permissionDecision": "deny"', blocked.stdout)

        warning = self.run_hook("secret_guard.py", {
            "hook_event_name": "PostToolUse",
            "session_id": "session-1",
            "tool_name": "Bash",
            "tool_input": {"command": "python -c print(token)"},
            "tool_response": {"stdout": "sk-aaaaaaaaaaaaaaaaaaaa", "stderr": ""},
        })
        self.assertEqual(warning.returncode, 0)
        self.assertIn("secret_guard 警告", warning.stdout)


if __name__ == "__main__":
    unittest.main()
