"""Exercise generation boundaries with real, disposable Git repositories."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]


class GenerationSafetyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="harness-generation-safety-")
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name).resolve()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith("GIT_")}
        self.env.update(HOME=str(self.base), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.repo = self.base / "original"
        self.repo.mkdir()
        self.run_command("git", "init", "-q", str(self.repo))

    def run_command(self, *args):
        return subprocess.run(args, env=self.env, capture_output=True, text=True, check=True)

    def snapshot(self, root, exclude=None):
        return {str(path.relative_to(root)): (
            path.lstat().st_mode,
            str(path.readlink()) if path.is_symlink() else
            path.read_bytes() if path.is_file() else None,
        ) for path in root.rglob("*")
            if exclude is None or not path.is_relative_to(exclude)}

    def test_nested_candidate_does_not_change_parent_repository(self):
        for configured in (False, True):
            with self.subTest(configured_hooks=configured):
                if configured:
                    self.run_command("git", "-C", str(self.repo), "config", "core.hooksPath", "custom-hooks")
                candidate = self.repo / ("configured" if configured else "default")
                candidate.mkdir()
                before = self.snapshot(self.repo, exclude=candidate)
                result = self.run_command("bash", str(SCRIPTS / "build_harness.sh"), str(candidate))
                self.assertTrue((candidate / "AGENTS.md").is_file())
                self.assertEqual(self.snapshot(self.repo, exclude=candidate), before)
                self.assertIn("[SKIP]", result.stdout)

    def test_linked_worktree_does_not_change_shared_repository_or_hooks(self):
        self.run_command("git", "-C", str(self.repo), "-c", "user.name=Fixture", "-c",
                         "user.email=fixture@example.test", "commit", "--allow-empty", "-qm", "fixture")
        worktree = self.base / "worktree"
        self.run_command("git", "-C", str(self.repo), "worktree", "add", "--detach", str(worktree))
        before = self.snapshot(self.repo)
        result = self.run_command("bash", str(SCRIPTS / "build_harness.sh"), str(worktree))
        self.assertTrue((worktree / "AGENTS.md").is_file())
        self.assertEqual(self.snapshot(self.repo), before)
        self.assertIn("[SKIP]", result.stdout)

    def test_root_setup_preserves_existing_hook_and_configuration(self):
        existing = self.repo / ".git/hooks/commit-msg"
        existing.write_text("#!/bin/sh\nexit 7\n")
        existing.chmod(0o755)
        self.run_command("git", "-C", str(self.repo), "config", "core.hooksPath", "custom-hooks")
        before_git = self.snapshot(self.repo / ".git")
        result = self.run_command("bash", str(SCRIPTS / "setup_hooks.sh"), str(self.repo))
        self.assertTrue((self.repo / "scripts/pre_commit_check.sh").is_file())
        self.assertEqual(self.snapshot(self.repo / ".git"), before_git)
        self.assertIn("[KEEP] core.hooksPath=custom-hooks", result.stdout)

    def test_root_setup_retains_supported_activation_behavior(self):
        result = self.run_command("bash", str(SCRIPTS / "setup_hooks.sh"), str(self.repo))
        self.assertTrue((self.repo / ".git/hooks/commit-msg").is_symlink())
        self.assertFalse((self.repo / ".git/hooks/pre-commit").exists())
        self.assertFalse((self.repo / ".git/hooks/pre-push").exists())
        self.assertIn("[PENDING]", result.stdout)
        before = self.snapshot(self.repo)
        self.run_command("bash", str(SCRIPTS / "setup_hooks.sh"), str(self.repo))
        self.assertEqual(self.snapshot(self.repo), before)

    def test_flat_legacy_documents_block_before_writing_and_are_preserved_on_acceptance(self):
        mappings = {
            "database.md": "data/database.md", "api-standards.md": "contracts/api-standards.md",
            "development.md": "devops/local-dev.md", "env.md": "devops/local-dev.md",
            "local-dev.md": "devops/local-dev.md", "deployment.md": "devops/release.md",
            "release.md": "devops/release.md",
        }
        for name, destination in mappings.items():
            for linked in (False, True):
                with self.subTest(name=name, dangling_link=linked):
                    target = self.base / (name + ("-link" if linked else "-file"))
                    legacy = target / ".harness/docs" / name
                    legacy.parent.mkdir(parents=True)
                    if linked:
                        legacy.symlink_to("missing-source")
                    else:
                        legacy.write_bytes(b"Keep legacy facts\r\n")
                    before = self.snapshot(target)
                    command = ["bash", str(SCRIPTS / "build_harness.sh"), str(target)]
                    result = subprocess.run(command, env=self.env, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                    self.assertEqual(self.snapshot(target), before)
                    self.run_command(*command, "--accept-migrations")
                    self.assertEqual(self.snapshot(target)[str(legacy.relative_to(target))],
                                     before[str(legacy.relative_to(target))])
                    self.assertFalse((target / ".harness/docs" / destination).exists())


if __name__ == "__main__":
    unittest.main()
